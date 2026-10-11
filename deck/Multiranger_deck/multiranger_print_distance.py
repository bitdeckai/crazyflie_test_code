"""打印 Crazyflie Multi-ranger Deck 的测距数据。

运行前安装 Bitcraze 官方 Python 库：

    pip install cflib

将下方 ``URI`` 的默认值修改为实际使用的 Crazyradio 配置，或者通过
``CFLIB_URI`` 环境变量指定连接地址。程序每 100 ms 打印一次数据，距离
单位为米；没有有效测距值时显示 ``None``。

PowerShell 运行示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Multiranger_deck\multiranger_print_distance.py

按 Ctrl+C 停止程序。如果出现 ``KeyError: Variable range.front not in TOC``，
请检查 Crazyflie 固件版本，以及 Multi-ranger Deck 是否已被正确识别。

数据判定参考：

正常判据：
- front/back/left/right/up/down 多数时间返回有效距离（单位 m）。
- 静止时各方向距离仅小幅波动。
- 在某一方向靠近障碍物时，对应方向距离持续减小，远离时回升。

异常判据：
- 多个方向长期为 None 或固定异常值。
- 静止状态下距离大幅抖动且无规律。
- 移动到障碍物附近时对应方向距离无明显变化。

官方库：https://github.com/bitcraze/crazyflie-lib-python
"""

import time
import logging
import cflib.crtp

from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.utils.multiranger import Multiranger

URI = uri_helper.uri_from_env(
    default='radio://0/80/2M/E7E7E7E7E7'
)

logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(
        URI, cf=Crazyflie(rw_cache='./cache')
    ) as scf:
        with Multiranger(scf) as mr:
            print("Multi-ranger test started. Ctrl+C to stop.")

            try:
                while True:
                    print(
                        f"Front: {mr.front!s:>6} m | "
                        f"Back: {mr.back!s:>6} m | "
                        f"Left: {mr.left!s:>6} m | "
                        f"Right: {mr.right!s:>6} m | "
                        f"Up: {mr.up!s:>6} m | "
                        f"Down: {mr.down!s:>6} m"
                    )
                    time.sleep(0.1)

            except KeyboardInterrupt:
                print("\nTest stopped.")
