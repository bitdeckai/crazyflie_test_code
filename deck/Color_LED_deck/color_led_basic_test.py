"""Color LED Deck 基础测试：切换颜色并打印温度/电流日志。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Color_LED_deck\color_led_basic_test.py

数据判定参考：

正常判据：
- WRGB 切换后颜色与设置一致（红、绿、蓝、白、灰阶都可见）。
- deckTemp 变化平稳，无持续快速上升。
- throttlePct 常见接近 0，短时波动后可回落。
- ledCurR/G/B/W 为非负值，且和点亮颜色对应。

异常判据：
- 颜色切换明显不对应，或某通道始终无响应。
- throttlePct 长时间高于 0，伴随亮度被限制。
- 电流读数异常抖动或明显不合理（例如点亮后仍长期接近 0）。
"""

import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.utils import uri_helper


URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

logging.basicConfig(level=logging.ERROR)


def _attached_color_groups(scf):
    deck_values = scf.cf.param.toc.toc.get('deck', {})
    groups = []

    if 'bcColorLedBot' in deck_values and int(scf.cf.param.get_value('deck.bcColorLedBot')):
        groups.append('colorLedBot')
    if 'bcColorLedTop' in deck_values and int(scf.cf.param.get_value('deck.bcColorLedTop')):
        groups.append('colorLedTop')

    return groups


def _set_wrgb(cf, group, wrgb):
    cf.param.set_value(f'{group}.wrgb8888', wrgb)


def _log_once(scf, group):
    log_conf = LogConfig(name=f'{group}Status', period_in_ms=200)
    log_conf.add_variable(f'{group}.deckTemp')
    log_conf.add_variable(f'{group}.throttlePct')
    log_conf.add_variable(f'{group}.ledCurR')
    log_conf.add_variable(f'{group}.ledCurG')
    log_conf.add_variable(f'{group}.ledCurB')
    log_conf.add_variable(f'{group}.ledCurW')

    with SyncLogger(scf, log_conf) as logger:
        for _, data, _ in logger:
            print(
                f"{group}: T={data[f'{group}.deckTemp']} C, "
                f"throttle={data[f'{group}.throttlePct']}%, "
                f"I(mA)=R:{data[f'{group}.ledCurR']} "
                f"G:{data[f'{group}.ledCurG']} "
                f"B:{data[f'{group}.ledCurB']} "
                f"W:{data[f'{group}.ledCurW']}"
            )
            break


def main():
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        scf.wait_for_params()
        groups = _attached_color_groups(scf)

        if not groups:
            raise RuntimeError('固件未识别到 Color LED Deck（top 或 bottom）。')

        print('Detected:', ', '.join(groups))

        # WRGB format: 0xWWRRGGBB
        pattern = [
            0x00000000,
            0x00FF0000,
            0x0000FF00,
            0x000000FF,
            0xFF000000,
            0x00777777,
        ]

        originals = {
            group: scf.cf.param.get_value(f'{group}.wrgb8888')
            for group in groups
        }

        try:
            for group in groups:
                scf.cf.param.set_value(f'{group}.brightCorr', 1)

            for color in pattern:
                for group in groups:
                    _set_wrgb(scf.cf, group, color)
                print(f'Set WRGB: 0x{color:08X}')
                time.sleep(1.0)

            for group in groups:
                _log_once(scf, group)
        finally:
            for group, value in originals.items():
                scf.cf.param.set_value(f'{group}.wrgb8888', value)
            print('Color restored to original values.')


if __name__ == '__main__':
    main()
