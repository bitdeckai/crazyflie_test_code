"""Prototyping Deck 基础检查：连通与 deck 参数扫描。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Prototyping_deck\prototyping_basic_test.py

说明：Prototyping Deck 是扩展底板，通常没有统一的官方参数/日志。
此脚本用于确认链路和 deck 参数读取正常。

数据判定参考：

正常判据：
- 连接稳定，deck 参数读取正常。
- 你的自定义外设在主控程序中可稳定响应。
- 多次上电后识别结果一致。

异常判据：
- deck 识别结果在多次上电间不一致。
- 外设响应不稳定或对相同输入结果随机。
- 参数读取偶发超时，提示供电或连线问题。
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

        print('Prototyping Deck 的功能取决于你自定义电路，需按应用自行写测试项。')


if __name__ == '__main__':
    main()
