"""列出 Crazyflie 固件已识别的扩展 Deck。

安装依赖并在 PowerShell 中运行：

    pip install cflib
    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\detect_attached_decks.py

脚本只读取 ``deck.*`` 参数，不会启动电机或修改 Crazyflie 配置。

数据判定参考：

正常判据：
- 已安装的 Deck 对应 deck.bc* 参数为 1。
- 多次运行脚本，识别结果基本一致。

异常判据：
- 已安装 Deck 对应参数长期为 0。
- 同一硬件连接条件下，识别结果频繁变化。
- 完全无 Deck 被识别，需检查接触、供电与固件版本。
"""

import logging

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper


URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

DECK_NAMES = {
    'bcActiveMarker': 'Active Marker Deck',
    'bcBigQuad': 'BigQuad Deck',
    'bcBuzzer': 'Buzzer Deck',
    'bcColorLedBot': 'Color LED Deck (bottom)',
    'bcColorLedTop': 'Color LED Deck (top)',
    'bcFlow': 'Flow Deck v1',
    'bcFlow2': 'Flow Deck v2',
    'bcLedRing': 'LED-ring Deck',
    'bcLighthouse4': 'Lighthouse Positioning Deck',
    'bcLoco': 'Loco Positioning Deck',
    'bcMultiRanger': 'Multi-ranger Deck',
    'bcUSD': 'Micro SD Card Deck',
    'bcZRanger': 'Z-ranger Deck v1',
    'bcZRanger2': 'Z-ranger Deck v2',
}

logging.basicConfig(level=logging.ERROR)


def main():
    cflib.crtp.init_drivers()

    with SyncCrazyflie(
        URI, cf=Crazyflie(rw_cache='./cache')
    ) as scf:
        scf.wait_for_params()
        deck_params = scf.cf.param.toc.toc.get('deck', {})
        attached = []

        for param_name in sorted(deck_params):
            if not param_name.startswith('bc'):
                continue

            value = scf.cf.param.get_value(f'deck.{param_name}')
            if int(float(value)) != 0:
                attached.append(param_name)

        if not attached:
            print('No supported Deck was reported by the firmware.')
            print('Check the Deck connection and update the Crazyflie firmware.')
            return

        print('Detected Decks:')
        for param_name in attached:
            display_name = DECK_NAMES.get(param_name, param_name)
            print(f'  - {display_name} (deck.{param_name})')


if __name__ == '__main__':
    main()