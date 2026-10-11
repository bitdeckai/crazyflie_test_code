# crazyflie_test_code

Crazyflie Deck 的基础测试脚本集合（以地面连通性与数据读取为主，不包含起飞控制）。

## 快速开始

1. 安装依赖

```powershell
pip install cflib
```

2. 设置连接 URI（按你的 Crazyradio 配置修改）

```powershell
$env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
```

如果不做修改也可以，默认就是 radio://0/80/2M/E7E7E7E7E7

如果地址或者信道被修改了，可以修改成如下：

```powershell
$env:CFLIB_URI = "radio://0/80/2M/E7E7E7E701"
```

也可以直接修改python脚本

3. 进入 deck 目录文档按需运行脚本

- 见 `deck/README.md`

## Crazyradio 基础测试

已提供脚本：

- `crazyradioPA/crazyradioPA_health_check.py`（放在 PA 目录下的入口）
- `crazyradio2.0/crazyradio2_0_health_check.py`（放在 2.0 目录下的入口）

用途：

- 扫描本机可见的 Crazyradio（如 `radio0`、`radio1`）
- 按地址探测飞控是否可达
- 可选验证指定 URI 的端到端连通

地址规则：

- 默认地址：`E7E7E7E7E7`
- 多飞控分配：`E7E7E7E701`、`E7E7E7E702`

PowerShell 示例：

```powershell
# 基础扫描
python .\crazyradioPA\crazyradioPA_health_check.py
python .\crazyradio2.0\crazyradio2_0_health_check.py

# 你有 2 个 radio 时，要求至少识别 2 个 dongle
python .\crazyradioPA\crazyradioPA_health_check.py --expect-radios 2

# 同时验证两个 URI（radio0 和 radio1）
python .\crazyradio2.0\crazyradio2_0_health_check.py --expect-radios 2 --verify-uri radio://0/80/2M/E7E7E7E701 --verify-uri radio://1/80/2M/E7E7E7E702
```

## 飞行器本体基础测试（不解锁电机，不起飞）

你创建的三个机体目录都已提供基础测试脚本：

- `crazyflie2.1/cf21_basic_health_check.py`
- `crazyflie2.1_brushless/cf21_brushless_basic_health_check.py`
- `crazyflie_bot/cf_bot_basic_health_check.py`

每个脚本都支持两种指定连接地址的方式：

1. 通过专用环境变量（推荐）
2. 通过 `--uri` 参数临时指定

两个 Crazyradio 的 URI 写法示例：

- Radio 0: `radio://0/80/2M/E7E7E7E7E7`
- Radio 1: `radio://1/80/2M/E7E7E7E7E7`

多个飞控地址分配规则：

- 默认地址统一使用：`E7E7E7E7E7`
- 多飞控时从以下地址开始分配：
	- 第 1 台：`E7E7E7E701`
	- 第 2 台：`E7E7E7E702`

PowerShell 示例：

```powershell
# Crazyflie 2.1（Radio 0）
$env:CFLIB_URI_CF21 = "radio://0/80/2M/E7E7E7E7E7"
python .\crazyflie2.1\cf21_basic_health_check.py

# Crazyflie 2.1 Brushless（Radio 1）
$env:CFLIB_URI_CF21_BRUSHLESS = "radio://1/80/2M/E7E7E7E702"
python .\crazyflie2.1_brushless\cf21_brushless_basic_health_check.py

# Crazyflie Bot（通过 --uri 临时指定 Radio 0）
python .\crazyflie_bot\cf_bot_basic_health_check.py --uri radio://0/80/2M/E7E7E7E701
```

日志会优先输出：

- 电源状态：`pm.vbat`、`pm.batteryLevel`、`pm.state`
- 姿态状态：`stabilizer.roll`、`stabilizer.pitch`、`stabilizer.yaw`
- 位置估计：`stateEstimate.x`、`stateEstimate.y`、`stateEstimate.z`
- 已识别 deck 标志：`deck.bc*`

## 说明

- 每个 deck 脚本顶部都包含“数据判定参考”，并使用更正式术语：
	- 正常判据
	- 异常判据
- 这些脚本用于快速检查 Deck 是否被识别、参数/日志是否正常，不会主动解锁电机。
