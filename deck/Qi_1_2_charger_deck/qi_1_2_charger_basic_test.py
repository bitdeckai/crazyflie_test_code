"""Qi 1.2 Charger Deck 基础检查：连通与 deck 参数扫描。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Qi_1_2_charger_deck\qi_1_2_charger_basic_test.py

说明：Qi 充电 Deck 通常是供电类外设，无公开通用参数/日志接口。
此脚本用于确认连接可用并输出当前固件识别到的 deck.* 状态。

数据判定参考：

正常判据：
- 连接稳定，deck 参数可完整读取。
- 与 Qi 相关 deck 标志位为 1（若固件提供对应标志）。
- 放上无线充电底座后，供电行为或指示状态符合预期。

异常判据：
- deck 参数读取失败或连接频繁中断。
- 已正确安装但相关 deck 标志位长期为 0。
- 放上充电底座后无任何供电变化或存在明显不稳定。
"""

import logging

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper


URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

logging.basicConfig(level=logging.ERROR)


def main():
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        scf.wait_for_params()
        print('Connected. Current deck.* flags:')

        for name in sorted(scf.cf.param.toc.toc.get('deck', {})):
            if not name.startswith('bc'):
                continue
            value = scf.cf.param.get_value(f'deck.{name}')
            print(f'  deck.{name} = {value}')

        print('Qi Deck 无专用 host 参数时，可通过硬件指示灯/供电行为做人工验证。')


if __name__ == '__main__':
    main()
