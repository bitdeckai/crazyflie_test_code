"""BigQuad Deck 基础测试：检测 deck，并读取外接电源监测数据（如果可用）。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\BigQuad_deck\bigquad_basic_test.py

说明：脚本不发送电机命令，仅做地面只读检查。

数据判定参考：

正常判据：
- deck.bcBigQuad 为 1，且可稳定连接。
- 若启用 asc37800 日志，V、I、P 数值稳定且与供电状态一致。
- 静止状态下电压波动小，电流和功率在合理范围。

异常判据：
- deck.bcBigQuad 为 0 或连接不稳定。
- 明确启用电源监测后仍无 asc37800 日志组。
- 电压、电流、功率长期异常跳变或明显不合理。
"""

import logging

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

        if 'bcBigQuad' not in scf.cf.param.toc.toc.get('deck', {}):
            raise RuntimeError('缺少参数 deck.bcBigQuad，请先升级 Crazyflie 固件。')
        if int(scf.cf.param.get_value('deck.bcBigQuad')) == 0:
            raise RuntimeError('固件未识别到 BigQuad Deck。')

        print('BigQuad deck detected.')

        if 'asc37800' not in scf.cf.log.toc.toc:
            print('未发现 asc37800 日志组，当前固件可能未启用外接电源监测。')
            return

        log_conf = LogConfig(name='BigQuadPower', period_in_ms=200)
        log_conf.add_variable('asc37800.v_mV')
        log_conf.add_variable('asc37800.i_mA')
        log_conf.add_variable('asc37800.p_mW')

        print('Power monitor test started. Ctrl+C to stop.')
        try:
            with SyncLogger(scf, log_conf) as logger:
                for _, data, _ in logger:
                    print(
                        f"V={data['asc37800.v_mV']} mV | "
                        f"I={data['asc37800.i_mA']} mA | "
                        f"P={data['asc37800.p_mW']} mW"
                    )
        except KeyboardInterrupt:
            print('\nTest stopped.')


if __name__ == '__main__':
    main()
