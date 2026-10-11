"""Crazyradio PA health check utility.

Purpose:
- Verify Crazyradio dongles are visible (radio://0, radio://1, ...)
- Probe common Crazyflie addresses
- Optionally verify end-to-end connection for specific URIs

Address rules used in this project:
- Default single-controller address: E7E7E7E7E7
- Multi-controller allocation starts from:
  - E7E7E7E701
  - E7E7E7E702

Examples (PowerShell):

    # Scan dongles and probe default + multi-controller addresses
    python .\crazyradioPA\crazyradioPA_health_check.py

    # Require 2 Crazyradio dongles (radio0 and radio1)
    python .\crazyradioPA\crazyradioPA_health_check.py --expect-radios 2

    # Also verify direct URI connectivity
    python .\crazyradioPA\crazyradioPA_health_check.py --verify-uri radio://0/80/2M/E7E7E7E701 --verify-uri radio://1/80/2M/E7E7E7E702
"""

from __future__ import annotations

import argparse
from typing import Iterable, List, Tuple

import cflib.crtp


DEFAULT_ADDRS = [
    "E7E7E7E7E7",
    "E7E7E7E701",
    "E7E7E7E702",
]


def _parse_hex_address(text: str) -> int:
    value = text.strip().upper()
    if value.startswith("0X"):
        value = value[2:]
    if len(value) == 0 or len(value) > 10:
        raise ValueError(f"Invalid address '{text}'")
    return int(value, 16)


def _format_hex_address(address: int) -> str:
    return f"{address:010X}"


def _extract_radio_index(uri: str) -> int | None:
    if not uri.startswith("radio://"):
        return None
    try:
        tail = uri.split("://", 1)[1]
        return int(tail.split("/", 1)[0])
    except (ValueError, IndexError):
        return None


def _scan_dongles() -> Tuple[List[List[str]], List[int]]:
    interfaces = cflib.crtp.scan_interfaces()
    radios = []
    for entry in interfaces:
        if not entry:
            continue
        uri = entry[0]
        radio_idx = _extract_radio_index(uri)
        if radio_idx is not None:
            radios.append(radio_idx)
    return interfaces, sorted(set(radios))


def _probe_address(address: int) -> List[List[str]]:
    return cflib.crtp.scan_interfaces(address=address)


def _render_probe_uris(scan_rows: Iterable[List[str]], address: int) -> List[str]:
    addr_hex = _format_hex_address(address)
    uris = []
    for row in scan_rows:
        if not row:
            continue
        base_uri = row[0]
        if not base_uri.startswith("radio://"):
            continue
        uris.append(f"{base_uri}/{addr_hex}")
    return uris


def _verify_uri(uri: str) -> Tuple[bool, str]:
    from cflib.crazyflie import Crazyflie
    from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

    try:
        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache="./cache")) as scf:
            scf.wait_for_params()
        return True, "Connected and parameters loaded"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Crazyradio PA health check")
    parser.add_argument(
        "--addresses",
        default=",".join(DEFAULT_ADDRS),
        help="Comma-separated hex addresses to probe",
    )
    parser.add_argument(
        "--expect-radios",
        type=int,
        default=None,
        help="Expected number of Crazyradio dongles (for pass/fail check)",
    )
    parser.add_argument(
        "--verify-uri",
        action="append",
        default=[],
        help="Optional: verify end-to-end connection for this URI (repeatable)",
    )
    args = parser.parse_args()

    addresses = []
    for part in args.addresses.split(","):
        part = part.strip()
        if not part:
            continue
        addresses.append(_parse_hex_address(part))

    print("Initializing CRTP drivers...")
    cflib.crtp.init_drivers()

    ok = True

    interfaces, radios = _scan_dongles()
    print("\n[Scan] Visible radio interfaces:")
    if interfaces:
        for row in interfaces:
            uri = row[0] if row else "<unknown>"
            note = row[1] if len(row) > 1 else ""
            print(f"  - {uri} {note}".rstrip())
    else:
        print("  - none")

    if radios:
        printable = ", ".join(f"radio{idx}" for idx in radios)
        print(f"Detected Crazyradio dongles: {printable}")
    else:
        print("Detected Crazyradio dongles: none")
        ok = False

    if args.expect_radios is not None and len(radios) < args.expect_radios:
        print(
            f"[FAIL] expected at least {args.expect_radios} dongles, found {len(radios)}"
        )
        ok = False

    print("\n[Probe] Crazyflie addresses:")
    for address in addresses:
        hits = _probe_address(address)
        addr_hex = _format_hex_address(address)
        if not hits:
            print(f"  - {addr_hex}: not reachable")
            continue

        probe_uris = _render_probe_uris(hits, address)
        print(f"  - {addr_hex}: reachable")
        for uri in probe_uris:
            print(f"      * {uri}")

    if args.verify_uri:
        print("\n[Verify] End-to-end URI connectivity:")
        for uri in args.verify_uri:
            status, message = _verify_uri(uri)
            if status:
                print(f"  - [OK] {uri}: {message}")
            else:
                print(f"  - [FAIL] {uri}: {message}")
                ok = False

    print("\nResult:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
