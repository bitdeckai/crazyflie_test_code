# deck 测试脚本

先安装官方库：

```powershell
pip install cflib
```

建议先设置 URI：

```powershell
$env:CFLIB_URI = "radio://0/80/2M/E7E7E7E7E7"
```

## 通用识别

```powershell
python .\deck\detect_attached_decks.py
```

## 功能性 Deck

```powershell
python .\deck\Flow_deck_v2\flow_print_data.py
python .\deck\LED_ring_deck\led_ring_basic_test.py
python .\deck\Color_LED_deck\color_led_basic_test.py
python .\deck\Micro_SD_card_deck\micro_sd_basic_test.py
python .\deck\Active_marker_deck\active_marker_basic_test.py
python .\deck\Motion_capture_marker_deck\motion_capture_marker_basic_test.py
python .\deck\Loco_positioning_deck\loco_basic_test.py
python .\deck\Lighthouse_positioning_deck\lighthouse_basic_test.py
python .\deck\BigQuad_deck\bigquad_basic_test.py
python .\deck\Buzzer_deck\buzzer_basic_test.py
```

## 无统一官方 API 的 Deck

```powershell
python .\deck\Qi_1_2_charger_deck\qi_1_2_charger_basic_test.py
python .\deck\Prototyping_deck\prototyping_basic_test.py
python .\deck\Breakout_deck\breakout_basic_test.py
```

说明：Multi-ranger 你已经有脚本，保留原目录即可。
