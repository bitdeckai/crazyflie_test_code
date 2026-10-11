"""Lighthouse Positioning Deck 基础测试：读取可见基站角度帧。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Lighthouse_positioning_deck\lighthouse_basic_test.py

说明：如果附近没有 Lighthouse 基站，frames/s 可能为 0。

数据判定参考：

正常判据：
- 有基站工作时 frames/s 持续大于 0。
- visible_base_stations 能稳定显示 1 个或多个基站编号。
- 轻微移动机体后，仍能持续收到角度帧。

异常判据：
- 明确有基站在工作，但 frames/s 长期为 0。
- 可见基站列表频繁丢失并长时间为 None。
- 稍微移动就完全无帧，提示视场、遮挡或同步问题。
"""

import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.localization.lighthouse_sweep_angle_reader import LighthouseSweepAngleReader
from cflib.utils import uri_helper


URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

logging.basicConfig(level=logging.ERROR)


def main():
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        scf.wait_for_params()

        if 'bcLighthouse4' not in scf.cf.param.toc.toc.get('deck', {}):
            raise RuntimeError('缺少参数 deck.bcLighthouse4，请先升级 Crazyflie 固件。')
        if int(scf.cf.param.get_value('deck.bcLighthouse4')) == 0:
            raise RuntimeError('固件未识别到 Lighthouse Positioning Deck。')

        frame_counter = 0
        visible_bs = set()

        def on_sweep(base_station_id, _angles):
            nonlocal frame_counter
            frame_counter += 1
            visible_bs.add(base_station_id)

        reader = LighthouseSweepAngleReader(scf.cf, on_sweep)
        reader.start()

        print('Lighthouse test started. Ctrl+C to stop.')
        try:
            while True:
                prev = frame_counter
                time.sleep(1.0)
                fps = frame_counter - prev
                seen = ','.join(str(i + 1) for i in sorted(visible_bs))
                if not seen:
                    seen = 'None'
                print(f'frames/s={fps:3} | visible_base_stations={seen}')
                visible_bs.clear()
        except KeyboardInterrupt:
            print('\nTest stopped.')
        finally:
            reader.stop()


if __name__ == '__main__':
    main()
