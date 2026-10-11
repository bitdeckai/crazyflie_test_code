"""Buzzer Deck 基础测试：检测 Deck 是否被固件识别。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Buzzer_deck\buzzer_basic_test.py

说明：官方固件未提供直接的蜂鸣器参数控制接口，此脚本做识别与连通性检查。

数据判定参考：

正常判据：
- deck.bcBuzzer 为 1，连接与参数读取稳定。
- 脚本可稳定输出 Buzzer Deck detected。

异常判据：
- deck.bcBuzzer 为 0，或频繁连不上。
- 参数 TOC 缺失 deck.bcBuzzer，通常表示固件版本不匹配。
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

        if 'bcBuzzer' not in scf.cf.param.toc.toc.get('deck', {}):
            raise RuntimeError('缺少参数 deck.bcBuzzer，请先升级 Crazyflie 固件。')

        attached = int(scf.cf.param.get_value('deck.bcBuzzer'))
        if attached == 0:
            raise RuntimeError('固件未识别到 Buzzer Deck。')

        print('Buzzer Deck detected.')
        print('提示：蜂鸣器的开关控制由固件内部模块使用，未暴露通用参数。')


if __name__ == '__main__':
    main()
