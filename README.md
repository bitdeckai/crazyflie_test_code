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

如果地址或者信道被修改了，可以修改成如下肢

```powershell
$env:CFLIB_URI = "radio://0/80/2M/E7E7E7E701"
```

也可以直接修改python脚本

3. 进入 deck 目录文档按需运行脚本

- 见 `deck/README.md`

## 说明

- 每个 deck 脚本顶部都包含“数据判定参考”，并使用更正式术语：
	- 正常判据
	- 异常判据
- 这些脚本用于快速检查 Deck 是否被识别、参数/日志是否正常，不会主动解锁电机。
