"""Crazyflie Bot basic health check (no arming, no flight).

Usage examples (PowerShell):

    # Default address (single flight controller)
    $env:CFLIB_URI_CFBOT = "radio://0/80/2M/E7E7E7E7E7"
    python .\crazyflie_bot\cf_bot_basic_health_check.py

    # Multiple flight controllers: allocate addresses from ...701, ...702
    $env:CFLIB_URI_CFBOT = "radio://0/80/2M/E7E7E7E701"
    python .\crazyflie_bot\cf_bot_basic_health_check.py

    $env:CFLIB_URI_CFBOT = "radio://1/80/2M/E7E7E7E702"
    python .\crazyflie_bot\cf_bot_basic_health_check.py

You can also pass --uri directly:

    python .\crazyflie_bot\cf_bot_basic_health_check.py --uri radio://1/80/2M/E7E7E7E702
"""

import argparse
import logging
import os

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger


DEFAULT_URI = "radio://0/80/2M/E7E7E7E7E7"
CUSTOM_URI_ENV = "CFLIB_URI_CFBOT"

logging.basicConfig(level=logging.ERROR)


def resolve_uri(cli_uri):
    if cli_uri:
        return cli_uri
    return os.getenv(CUSTOM_URI_ENV, os.getenv("CFLIB_URI", DEFAULT_URI))


def has_log_var(cf, full_name):
    group, name = full_name.split(".", 1)
    return name in cf.log.toc.toc.get(group, {})


def build_log_variables(scf):
    candidates = [
        "pm.vbat",
        "pm.batteryLevel",
        "pm.state",
        "stabilizer.roll",
        "stabilizer.pitch",
        "stabilizer.yaw",
        "stateEstimate.x",
        "stateEstimate.y",
        "stateEstimate.z",
    ]
    variables = [name for name in candidates if has_log_var(scf.cf, name)]
    if not variables:
        raise RuntimeError("No supported log variables found in firmware TOC.")
    return variables


def stream_log_blocks(scf, all_variables, samples_per_block):
    pending = [all_variables]
    last = {}
    block_no = 1

    while pending:
        variables = pending.pop(0)
        log_conf = LogConfig(name=f"CFBotBasic{block_no}", period_in_ms=200)
        for name in variables:
            log_conf.add_variable(name)

        try:
            print(f"Log block {block_no}: {', '.join(variables)}")
            with SyncLogger(scf, log_conf) as logger:
                for idx, (_, data, _) in enumerate(logger, start=1):
                    line = " | ".join(f"{name}={fmt(data[name])}" for name in variables)
                    print(f"[B{block_no:02d}-{idx:02d}] {line}")
                    last.update(data)
                    if idx >= samples_per_block:
                        break
        except AttributeError as error:
            if len(variables) <= 1:
                print(f"Skip log var {variables[0]}: {error}")
            else:
                split = len(variables) // 2
                left = variables[:split]
                right = variables[split:]
                print(
                    f"Log block too large, split into {len(left)} + {len(right)} variables."
                )
                pending.insert(0, right)
                pending.insert(0, left)
                continue

        block_no += 1

    return last


def print_decks(scf):
    deck_group = scf.cf.param.toc.toc.get("deck", {})
    attached = []
    for name in sorted(deck_group):
        if not name.startswith("bc"):
            continue
        value = int(float(scf.cf.param.get_value(f"deck.{name}")))
        if value != 0:
            attached.append(f"deck.{name}")

    if not attached:
        print("Detected deck flags: none")
        return

    print("Detected deck flags:")
    for item in attached:
        print(f"  - {item}")


def fmt(value):
    return f"{value:.3f}" if isinstance(value, float) else str(value)


def main():
    parser = argparse.ArgumentParser(description="Crazyflie Bot basic health check")
    parser.add_argument("--uri", default=None, help="Override URI, e.g. radio://1/80/2M/E7E7E7E702")
    parser.add_argument(
        "--samples",
        type=int,
        default=10,
        help="Number of log samples per log block",
    )
    args = parser.parse_args()

    uri = resolve_uri(args.uri)
    cflib.crtp.init_drivers()

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache="./cache")) as scf:
        scf.wait_for_params()
        print(f"Connected URI: {uri}")
        print_decks(scf)

        variables = build_log_variables(scf)
        print("Logging vars:", ", ".join(variables))
        print("Basic health log started. Ctrl+C to stop.")

        last = {}
        try:
            last = stream_log_blocks(scf, variables, args.samples)
        except KeyboardInterrupt:
            print("\nTest stopped by user.")

        if "pm.vbat" in last:
            if last["pm.vbat"] < 3.3:
                print("Warning: battery voltage is low (< 3.3V).")
            elif last["pm.vbat"] < 3.5:
                print("Notice: battery is usable but charging is recommended.")
            else:
                print("Battery voltage check looks normal.")


if __name__ == "__main__":
    main()
