"""Breakout Deck 基础检查：连通与 deck 参数扫描。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Breakout_deck\breakout_basic_test.py

说明：Breakout Deck 主要是引脚转接，通常没有统一官方参数/日志。
此脚本用于确认链路和 deck 参数读取正常。

数据判定参考：

正常判据：
- 连接与参数读取稳定。
- 外接器件在预期引脚上可稳定工作。
- 重复测试时结果一致。

异常判据：
- 连接稳定性差，参数读取偶发失败。
- 外接器件无响应或仅偶发响应。
- 不同上电周期表现差异大，提示接线或供电问题。
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

        print('Breakout Deck 的功能取决于外接器件，需按你的硬件连线写专项测试。')


if __name__ == '__main__':
    main()
