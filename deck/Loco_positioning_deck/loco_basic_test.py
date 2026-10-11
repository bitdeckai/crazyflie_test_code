"""Loco Positioning Deck 基础测试：打印模式与测距状态。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Loco_positioning_deck\loco_basic_test.py

说明：脚本只读取数据，不解锁电机。

数据判定参考：

正常判据：
- deckStatus.bcLoco 持续为 0。
- loco.mode 稳定在 1、2 或 3（对应 TWR、TDoA2、TDoA3）。
- ranging.state 在有锚点时非 0，且随可见锚点变化。

异常判据：
- deckStatus.bcLoco 非 0，说明定位链路异常。
- loco.mode 长时间不在 1 到 3。
- 已确认有锚点但 ranging.state 长期为 0。
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

        if 'bcLoco' not in scf.cf.param.toc.toc.get('deck', {}):
            raise RuntimeError('缺少参数 deck.bcLoco，请先升级 Crazyflie 固件。')
        if int(scf.cf.param.get_value('deck.bcLoco')) == 0:
            raise RuntimeError('固件未识别到 Loco Positioning Deck。')

        print('Loco test started. Ctrl+C to stop.')

        log_conf = LogConfig(name='Loco', period_in_ms=200)
        log_conf.add_variable('loco.mode')
        log_conf.add_variable('ranging.state')
        log_conf.add_variable('deckStatus.bcLoco')

        try:
            with SyncLogger(scf, log_conf) as logger:
                for _, data, _ in logger:
                    print(
                        f"mode={data['loco.mode']} | "
                        f"ranging.state={data['ranging.state']} | "
                        f"deckStatus={data['deckStatus.bcLoco']}"
                    )
        except KeyboardInterrupt:
            print('\nTest stopped.')
        except KeyError as error:
            raise RuntimeError(
                f'日志变量 {error} 不在 TOC 中，请检查固件版本。'
            ) from error


if __name__ == '__main__':
    main()
