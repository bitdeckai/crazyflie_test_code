"""Micro SD Card Deck 基础测试：检查状态、短时启动日志并读取速率。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Micro_SD_card_deck\micro_sd_basic_test.py

说明：此脚本会短时切换 usd.logging 参数，结束后恢复原状态。

数据判定参考：

正常判据：
- usd.canLog 为 1。
- 打开 usd.logging 后，spiWrBps、spiReBps、fatWrBps 出现稳定非零值。
- 恢复 original usd.logging 后不再持续增长写速率。

异常判据：
- usd.canLog 为 0，通常是 SD 卡或配置问题。
- 开启 logging 后三项速率长期为 0。
- 切回 original usd.logging 后仍持续高写入速率，或出现异常报错。
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


def main():
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        scf.wait_for_params()

        if 'bcUSD' not in scf.cf.param.toc.toc.get('deck', {}):
            raise RuntimeError('缺少参数 deck.bcUSD，请先升级 Crazyflie 固件。')
        if int(scf.cf.param.get_value('deck.bcUSD')) == 0:
            raise RuntimeError('固件未识别到 Micro SD Card Deck。')

        can_log = int(scf.cf.param.get_value('usd.canLog'))
        original_logging = scf.cf.param.get_value('usd.logging')

        print(f'usd.canLog = {can_log}')
        print(f'original usd.logging = {original_logging}')

        if can_log == 0:
            print('当前无法记录到 SD 卡，请检查卡是否插好以及 config.txt 是否正确。')
            return

        try:
            scf.cf.param.set_value('usd.logging', 1)
            print('Set usd.logging = 1')
            time.sleep(2.0)

            log_conf = LogConfig(name='USD', period_in_ms=200)
            log_conf.add_variable('usd.spiWrBps')
            log_conf.add_variable('usd.spiReBps')
            log_conf.add_variable('usd.fatWrBps')

            with SyncLogger(scf, log_conf) as logger:
                count = 0
                for _, data, _ in logger:
                    print(
                        f"spiWrBps={data['usd.spiWrBps']:7} | "
                        f"spiReBps={data['usd.spiReBps']:7} | "
                        f"fatWrBps={data['usd.fatWrBps']:7}"
                    )
                    count += 1
                    if count >= 15:
                        break
        finally:
            scf.cf.param.set_value('usd.logging', original_logging)
            print(f'Restored usd.logging = {original_logging}')


if __name__ == '__main__':
    main()
