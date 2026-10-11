"""Motion Capture Marker 基础测试。

Crazyflie 官方固件中该功能由 Active Marker Deck 实现，
此脚本会将 activeMarker.mode 暂时切换为 Qualisys 模式(3)并读取健康状态。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Motion_capture_marker_deck\motion_capture_marker_basic_test.py

数据判定参考：

正常判据：
- activeMarker.mode 能设置为 3（Qualisys 模式）且运行稳定。
- activeMarker.i2cOk 长时间为 1。
- activeMarker.btSns 对遮挡或触发动作有变化。
- 结束后可恢复到原始 mode。

异常判据：
- mode 设置为 3 失败或被回退。
- i2cOk 频繁为 0。
- btSns 始终固定且无响应。
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
        try:
            scf.cf.param.set_value('activeMarker.mode', 3)
            print('Set activeMarker.mode = 3 (Qualisys mode)')
            time.sleep(1.0)

            log_conf = LogConfig(name='MocapMarker', period_in_ms=200)
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
