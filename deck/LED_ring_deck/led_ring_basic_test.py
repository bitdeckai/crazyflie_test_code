"""LED-ring Deck 基础测试：切换灯效并恢复原状态。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\LED_ring_deck\led_ring_basic_test.py

数据判定参考：

正常判据：
- ring.effect 切换后 1 到 2 秒内灯效可见变化。
- solidRed、solidGreen、solidBlue 设置后颜色符合预期。
- 脚本退出后，灯效恢复到 original ring.effect。

异常判据：
- 参数写入无报错但灯效始终不变化。
- 某些颜色通道长期不亮或明显异常。
- 无法恢复 original ring.effect，或恢复后仍异常闪烁。
"""

import logging
import time

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

        if 'bcLedRing' not in scf.cf.param.toc.toc.get('deck', {}):
            raise RuntimeError('缺少参数 deck.bcLedRing，请先升级 Crazyflie 固件。')
        if int(scf.cf.param.get_value('deck.bcLedRing')) == 0:
            raise RuntimeError('固件未识别到 LED-ring Deck。')

        original_effect = scf.cf.param.get_value('ring.effect')
        print(f'Original ring.effect = {original_effect}')

        try:
            scf.cf.param.set_value('ring.solidRed', 40)
            scf.cf.param.set_value('ring.solidGreen', 40)
            scf.cf.param.set_value('ring.solidBlue', 40)

            effects = [1, 2, 7, 14, 15, 18, 0]
            for effect in effects:
                scf.cf.param.set_value('ring.effect', effect)
                print(f'Set ring.effect = {effect}')
                time.sleep(1.5)
        finally:
            scf.cf.param.set_value('ring.effect', original_effect)
            print(f'Restored ring.effect = {original_effect}')


if __name__ == '__main__':
    main()
