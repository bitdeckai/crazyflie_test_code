# deck 测试脚本

先安装官方库：

```powershell
pip install cflib
```

建议先设置 URI：

```powershell
$env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
```

说明：各脚本文件顶部都带有“数据判定参考”，统一使用“正常判据 / 异常判据”术语。

## 测试命令与先看日志信息

| 脚本 | 测试命令 | 先看日志信息 |
|---|---|---|
| 通用识别 | `python .\deck\detect_attached_decks.py` | `Detected Decks` 列表；`deck.bc*` 对应 Deck 是否为 1 |
| Multi-ranger | `python .\deck\Multiranger_deck\multiranger_print_distance.py` | `Front/Back/Left/Right/Up/Down` 6 向距离 |
| Flow Deck v2 | `python .\deck\Flow_deck_v2\flow_print_data.py` | `deltaX`、`deltaY`、`squal`、`down` |
| LED-ring | `python .\deck\LED_ring_deck\led_ring_basic_test.py` | `Set ring.effect = ...` 与 `Restored ring.effect = ...` |
| Color LED | `python .\deck\Color_LED_deck\color_led_basic_test.py` | `deckTemp`、`throttlePct`、`ledCurR/G/B/W` |
| Micro SD | `python .\deck\Micro_SD_card_deck\micro_sd_basic_test.py` | `usd.canLog`、`usd.logging`、`spiWrBps/spiReBps/fatWrBps` |
| Active Marker | `python .\deck\Active_marker_deck\active_marker_basic_test.py` | `activeMarker.mode`、`i2cOk`、`btSns`、恢复日志 |
| Motion Capture Marker | `python .\deck\Motion_capture_marker_deck\motion_capture_marker_basic_test.py` | `activeMarker.mode = 3`、`i2cOk`、`btSns` |
| Loco Positioning | `python .\deck\Loco_positioning_deck\loco_basic_test.py` | `loco.mode`、`ranging.state`、`deckStatus.bcLoco` |
| Lighthouse Positioning | `python .\deck\Lighthouse_positioning_deck\lighthouse_basic_test.py` | `frames/s`、`visible_base_stations` |
| BigQuad | `python .\deck\BigQuad_deck\bigquad_basic_test.py` | `BigQuad deck detected`、`V/I/P` 电源监测日志 |
| Buzzer | `python .\deck\Buzzer_deck\buzzer_basic_test.py` | `Buzzer Deck detected` |
| Qi 1.2 Charger | `python .\deck\Qi_1_2_charger_deck\qi_1_2_charger_basic_test.py` | `deck.*` 标志输出与供电行为 |
| Prototyping | `python .\deck\Prototyping_deck\prototyping_basic_test.py` | `deck.*` 标志输出与自定义外设响应 |
| Breakout | `python .\deck\Breakout_deck\breakout_basic_test.py` | `deck.*` 标志输出与外接器件响应 |

## 各脚本测试日志示例

### 1) 通用识别：detect_attached_decks.py

```text
Detected Decks:
	- Flow Deck v2 (deck.bcFlow2)
	- Multi-ranger Deck (deck.bcMultiRanger)
	- LED-ring Deck (deck.bcLedRing)
```

### 2) Multi-ranger：multiranger_print_distance.py

```text
Multi-ranger test started. Ctrl+C to stop.
Front:  1.24 m | Back:  2.05 m | Left:  0.86 m | Right:  0.91 m | Up:  2.03 m | Down:  0.12 m
Front:  1.22 m | Back:  2.05 m | Left:  0.85 m | Right:  0.90 m | Up:  2.03 m | Down:  0.12 m
```

### 3) Flow Deck v2：flow_print_data.py

```text
Flow Deck v2 test started. Ctrl+C to stop.
deltaX:      1 | deltaY:     -1 | squal:  72 | down: 0.118 m
deltaX:      0 | deltaY:      1 | squal:  75 | down: 0.119 m
```

### 4) LED-ring：led_ring_basic_test.py

```text
Original ring.effect = 0
Set ring.effect = 1
Set ring.effect = 2
Set ring.effect = 7
Restored ring.effect = 0
```

### 5) Color LED：color_led_basic_test.py

```text
Detected: colorLedTop
Set WRGB: 0x00FF0000
Set WRGB: 0x0000FF00
colorLedTop: T=35 C, throttle=0%, I(mA)=R:11 G:0 B:0 W:0
Color restored to original values.
```

### 6) Micro SD：micro_sd_basic_test.py

```text
usd.canLog = 1
original usd.logging = 0
Set usd.logging = 1
spiWrBps=   2048 | spiReBps=    320 | fatWrBps=    896
Restored usd.logging = 0
```

### 7) Active Marker：active_marker_basic_test.py

```text
Original activeMarker.mode = 0
Set activeMarker.mode = 0
Set activeMarker.mode = 1
Set activeMarker.mode = 2
Set activeMarker.mode = 3
i2cOk=1 | btSns=0
Restored activeMarker.mode = 0
```

### 8) Motion Capture Marker：motion_capture_marker_basic_test.py

```text
Set activeMarker.mode = 3 (Qualisys mode)
i2cOk=1 | btSns=0
i2cOk=1 | btSns=1
Restored activeMarker.mode = 0
```

### 9) Loco Positioning：loco_basic_test.py

```text
Loco test started. Ctrl+C to stop.
mode=2 | ranging.state=1 | deckStatus=0
mode=2 | ranging.state=3 | deckStatus=0
```

### 10) Lighthouse Positioning：lighthouse_basic_test.py

```text
Lighthouse test started. Ctrl+C to stop.
frames/s= 58 | visible_base_stations=1,2
frames/s= 61 | visible_base_stations=1,2
```

### 11) BigQuad：bigquad_basic_test.py

```text
BigQuad deck detected.
Power monitor test started. Ctrl+C to stop.
V=15080 mV | I=220 mA | P=3317 mW
V=15076 mV | I=218 mA | P=3286 mW
```

### 12) Buzzer：buzzer_basic_test.py

```text
Buzzer Deck detected.
提示：蜂鸣器的开关控制由固件内部模块使用，未暴露通用参数。
```

### 13) Qi 1.2 Charger：qi_1_2_charger_basic_test.py

```text
Connected. Current deck.* flags:
	deck.bcFlow2 = 1
	deck.bcMultiRanger = 1
	... (按当前安装 Deck 而变化)
Qi Deck 无专用 host 参数时，可通过硬件指示灯/供电行为做人工验证。
```

### 14) Prototyping：prototyping_basic_test.py

```text
Connected. Current deck.* flags:
	deck.bcFlow2 = 1
	deck.bcLedRing = 1
	... (按当前安装 Deck 而变化)
Prototyping Deck 的功能取决于你自定义电路，需按应用自行写测试项。
```

### 15) Breakout：breakout_basic_test.py

```text
Connected. Current deck.* flags:
	deck.bcLoco = 1
	deck.bcUSD = 0
	... (按当前安装 Deck 而变化)
Breakout Deck 的功能取决于外接器件，需按你的硬件连线写专项测试。
```

说明：以上是示例日志，实际数值会随固件版本、环境、传感器视场和供电状态变化。

## 可选：语法快速校验

```powershell
python -m compileall .\deck
```
