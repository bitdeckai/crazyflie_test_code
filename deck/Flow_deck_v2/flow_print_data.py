"""Flow Deck v2 基础测试：每 100 ms 打印光流与下视距离。

运行前：

    pip install cflib

PowerShell 示例：

    $env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
    python .\deck\Flow_deck_v2\flow_print_data.py

不会解锁电机，也不会起飞。

数据判定参考：

正常判据：
- squal 大部分时间大于 40，且常见在 60 到 120。
- 机体静止时 deltaX、deltaY 在 0 附近小幅波动。
- 缓慢移动机体时 deltaX、deltaY 会持续同号变化，反向移动时符号反转。
- down 持续输出有效距离（非 None），数值与实际高度同量级。

异常判据：
- squal 长时间小于 20，或频繁掉到 0。
- 机体静止时 deltaX、deltaY 长时间偏大或单边漂移。
- 移动机体时 deltaX、deltaY 变化杂乱且与方向无关。
- down 长时间为 None，或明显不符合实际高度。
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


def _distance_mm_to_m(distance_mm):
    if distance_mm <= 0 or distance_mm >= 5000:
        return None
    return distance_mm / 1000.0


def main():
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        scf.wait_for_params()

        if 'bcFlow2' not in scf.cf.param.toc.toc.get('deck', {}):
            raise RuntimeError('缺少参数 deck.bcFlow2，请先升级 Crazyflie 固件。')
        if int(scf.cf.param.get_value('deck.bcFlow2')) == 0:
            raise RuntimeError('固件未识别到 Flow Deck v2。')

        log_conf = LogConfig(name='FlowV2', period_in_ms=100)
        log_conf.add_variable('motion.deltaX')
        log_conf.add_variable('motion.deltaY')
        log_conf.add_variable('motion.squal')
        log_conf.add_variable('range.zrange')

        print('Flow Deck v2 test started. Ctrl+C to stop.')
        try:
            with SyncLogger(scf, log_conf) as logger:
                for _, data, _ in logger:
                    down_m = _distance_mm_to_m(data['range.zrange'])
                    print(
                        f"deltaX: {data['motion.deltaX']:6} | "
                        f"deltaY: {data['motion.deltaY']:6} | "
                        f"squal: {data['motion.squal']:3} | "
                        f"down: {down_m} m"
                    )
        except KeyboardInterrupt:
            print('\nTest stopped.')
        except KeyError as error:
            raise RuntimeError(
                f'日志变量 {error} 不在 TOC 中，请检查固件版本。'
            ) from error


if __name__ == '__main__':
    main()
