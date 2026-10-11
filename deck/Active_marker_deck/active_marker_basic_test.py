"""Active Marker Deck 基础测试：模式切换与健康状态读取。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Active_marker_deck\active_marker_basic_test.py

说明：会临时修改 activeMarker.mode，退出时恢复。

数据判定参考：

正常判据：
- activeMarker.mode 在 0、1、2、3 之间切换无报错。
- activeMarker.i2cOk 长时间为 1。
- activeMarker.btSns 在遮挡/按压传感器时有变化（不操作时可保持稳定）。
- 脚本结束后 mode 成功恢复。

异常判据：
- mode 切换报错，或写入后读值不变化。
- i2cOk 频繁为 0，提示 I2C 通信异常。
- btSns 始终固定且对环境变化无响应。
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

        if 'bcActiveMarker' not in scf.cf.param.toc.toc.get('deck', {}):
            raise RuntimeError('缺少参数 deck.bcActiveMarker，请先升级 Crazyflie 固件。')
        if int(scf.cf.param.get_value('deck.bcActiveMarker')) == 0:
            raise RuntimeError('固件未识别到 Active Marker Deck。')

        original_mode = scf.cf.param.get_value('activeMarker.mode')
        print(f'Original activeMarker.mode = {original_mode}')

        try:
            for mode in (0, 1, 2, 3):
                scf.cf.param.set_value('activeMarker.mode', mode)
                print(f'Set activeMarker.mode = {mode}')
                time.sleep(1.5)

            log_conf = LogConfig(name='ActiveMarker', period_in_ms=200)
            log_conf.add_variable('activeMarker.i2cOk')
            log_conf.add_variable('activeMarker.btSns')

            with SyncLogger(scf, log_conf) as logger:
                count = 0
                for _, data, _ in logger:
                    print(
                        f"i2cOk={data['activeMarker.i2cOk']} | "
                        f"btSns={data['activeMarker.btSns']}"
                    )
                    count += 1
                    if count >= 20:
                        break
        finally:
            scf.cf.param.set_value('activeMarker.mode', original_mode)
            print(f'Restored activeMarker.mode = {original_mode}')


if __name__ == '__main__':
    main()
