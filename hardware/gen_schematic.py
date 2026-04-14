import re
from pathlib import Path

import schemdraw
import schemdraw.elements as elm

SVG_PATH = str(Path(__file__).with_name("schematic.svg"))


def draw_pc817_box(d, cy, label="PC817", flip_lr=False):
    """PC817 を 4 ピンの箱として描画し、ピン座標を返す。
    flip_lr=False: 左上=Pin1, 左下=Pin2, 右下=Pin3, 右上=Pin4 (Pi→MB 向き)
    flip_lr=True:  左上=Pin4, 左下=Pin3, 右下=Pin2, 右上=Pin1 (MB→Pi 向き)
    """
    bx_l, bx_r = -1.5, 1.5
    bx_t, bx_b = cy + 1, cy - 1

    d += elm.Line().at((bx_l, bx_t)).to((bx_r, bx_t))
    d += elm.Line().at((bx_r, bx_t)).to((bx_r, bx_b))
    d += elm.Line().at((bx_r, bx_b)).to((bx_l, bx_b))
    d += elm.Line().at((bx_l, bx_b)).to((bx_l, bx_t))
    d += elm.Label().at((0, cy)).label(label, fontsize=10)

    left_top = (bx_l, cy + 0.5)
    left_bot = (bx_l, cy - 0.5)
    right_bot = (bx_r, cy - 0.5)
    right_top = (bx_r, cy + 0.5)

    if not flip_lr:
        nums = ("1", "2", "3", "4")
    else:
        nums = ("4", "3", "2", "1")

    d += elm.Label().at((bx_l + 0.3, cy + 0.5)).label(nums[0], fontsize=7, color="gray")
    d += elm.Label().at((bx_l + 0.3, cy - 0.5)).label(nums[1], fontsize=7, color="gray")
    d += elm.Label().at((bx_r - 0.3, cy - 0.5)).label(nums[2], fontsize=7, color="gray")
    d += elm.Label().at((bx_r - 0.3, cy + 0.5)).label(nums[3], fontsize=7, color="gray")

    return left_top, left_bot, right_bot, right_top, bx_l, bx_r


def draw_switch_section(d, cy, gpio_label, section_label, btn_label, header_label):
    """PWR_SW / RST_SW: 左 = Pi(Pin1/Pin2)、右 = MB(Pin4/Pin3)。"""
    d += elm.Label().at((0, cy + 2.5)).label(f"[ {section_label} ]", fontsize=13)
    lt, lb, rb, rt, bx_l, bx_r = draw_pc817_box(d, cy, flip_lr=False)
    # lt=Pin1, lb=Pin2, rb=Pin3, rt=Pin4

    # Pi 側: Pin1 ← 330Ω ← 3.3V
    d += elm.Line().at(lt).to((bx_l - 1, lt[1]))
    d += elm.Resistor().at((bx_l - 1, lt[1])).to((bx_l - 4, lt[1])).label("330Ω", loc="top", fontsize=9)
    d += elm.Line().at((bx_l - 4, lt[1])).to((bx_l - 5, lt[1]))
    d += elm.Dot(open=True).at((bx_l - 5, lt[1]))
    d += elm.Label().at((bx_l - 6.5, lt[1])).label("3.3V\n(Zero W)", fontsize=10)

    # Pin2 ← GPIO
    d += elm.Line().at(lb).to((bx_l - 5, lb[1]))
    d += elm.Dot(open=True).at((bx_l - 5, lb[1]))
    d += elm.Label().at((bx_l - 6.5, lb[1])).label(f"{gpio_label}\n(Zero W)", fontsize=10)

    # MB 側: Pin4 → header、物理ボタン並列
    d += elm.Line().at(rt).to((bx_r + 5, rt[1]))
    d += elm.Dot(open=True).at((bx_r + 5, rt[1]))
    d += elm.Label().at((bx_r + 6.5, rt[1])).label(f"{header_label}\n(MB)", fontsize=10)
    d += elm.Dot().at((bx_r + 3, rt[1]))
    d += elm.Label().at((bx_r + 3, rt[1] + 0.4)).label(btn_label, fontsize=9)

    btn_x = bx_r + 3
    d += elm.Line().at((btn_x, rt[1])).to((btn_x, rt[1] - 0.5))
    d += elm.Switch().at((btn_x, rt[1] - 0.5)).to((btn_x, rt[1] - 2.5))

    pin3_down_x = bx_r + 1.5
    d += elm.Line().at(rb).to((pin3_down_x, rb[1]))
    d += elm.Line().at((pin3_down_x, rb[1])).to((pin3_down_x, rt[1] - 3))
    d += elm.Line().at((pin3_down_x, rt[1] - 3)).to((btn_x, rt[1] - 3))
    d += elm.Line().at((btn_x, rt[1] - 2.5)).to((btn_x, rt[1] - 3))
    d += elm.Ground().at((btn_x, rt[1] - 3))
    d += elm.Label().at((btn_x, rt[1] - 4.0)).label("MB GND", fontsize=8)

def draw_input_section(d, cy, gpio_label, section_label, header_label, r_limit="1kΩ"):
    """PWR_LED / HDD_LED / SPEAKER: 左 = Pi(Pin4/Pin3), 右 = MB(Pin1/Pin2)。"""
    d += elm.Label().at((0, cy + 2.5)).label(f"[ {section_label} ]", fontsize=13)
    lt, lb, rb, rt, bx_l, bx_r = draw_pc817_box(d, cy, flip_lr=True)
    # lt=Pin4, lb=Pin3, rb=Pin2, rt=Pin1

    # ---- 左 = Pi 側 ----
    # Pin4(左上) ← Pi 3.3V
    d += elm.Line().at(lt).to((bx_l - 5, lt[1]))
    d += elm.Dot(open=True).at((bx_l - 5, lt[1]))
    d += elm.Label().at((bx_l - 6.5, lt[1])).label("3.3V\n(Zero W)", fontsize=10)

    # Pin3(左下) → GPIO 分岐 + プルダウン 10kΩ → Pi GND
    d += elm.Line().at(lb).to((bx_l - 5, lb[1]))
    d += elm.Dot(open=True).at((bx_l - 5, lb[1]))
    d += elm.Label().at((bx_l - 6.5, lb[1])).label(f"{gpio_label}\n(Zero W)", fontsize=10)
    d += elm.Dot().at((bx_l - 2, lb[1]))
    d += elm.Resistor().at((bx_l - 2, lb[1])).to((bx_l - 2, lb[1] - 2)).label("10kΩ", loc="right", fontsize=9)
    d += elm.Ground().at((bx_l - 2, lb[1] - 2))
    d += elm.Label().at((bx_l - 2, lb[1] - 3.0)).label("Pi GND", fontsize=8)

    # ---- 右 = MB 側 ----
    # Pin1(右上) ← 制限抵抗 ← header+(5V)
    d += elm.Line().at(rt).to((bx_r + 1, rt[1]))
    d += elm.Resistor().at((bx_r + 1, rt[1])).to((bx_r + 4, rt[1])).label(r_limit, loc="top", fontsize=9)
    d += elm.Line().at((bx_r + 4, rt[1])).to((bx_r + 5, rt[1]))
    d += elm.Dot(open=True).at((bx_r + 5, rt[1]))
    d += elm.Label().at((bx_r + 6.5, rt[1])).label(f"{header_label}\n(MB, 5V)", fontsize=10)

    # Pin2(右下) → MB GND
    d += elm.Line().at(rb).to((bx_r + 2, rb[1]))
    d += elm.Line().at((bx_r + 2, rb[1])).to((bx_r + 2, rb[1] - 1.2))
    d += elm.Ground().at((bx_r + 2, rb[1] - 1.2))
    d += elm.Label().at((bx_r + 2, rb[1] - 2.2)).label("MB GND", fontsize=8)


def draw_speaker_section(d, cy, gpio_label, section_label):
    """Speaker: マザボ側は「IDLE=HIGH(5V), ビープ=LOW駆動」の LOW アクティブ。
    他の入力系と同じ配線にすると IDLE 時に LED 常時点灯してしまうため、
    1 次側の電源を PWR_LED+ から拝借し、SPEAKER+ が LOW に落ちたときだけ
    PWR_LED+(5V) → 1kΩ → LED → SPEAKER+(0V) の経路で電流が流れるようにする。
    これによりビープ時のみ LED 点灯 → 2 次側導通 → GPIO=HIGH となり、
    他の入力系と同じ「HIGH=アクティブ」論理で扱える。"""
    d += elm.Label().at((0, cy + 2.5)).label(f"[ {section_label} ]", fontsize=13)
    lt, lb, rb, rt, bx_l, bx_r = draw_pc817_box(d, cy, flip_lr=True)
    # lt=Pin4, lb=Pin3, rb=Pin2, rt=Pin1

    # ---- 左 = Pi 側(他の入力系と同じ) ----
    d += elm.Line().at(lt).to((bx_l - 5, lt[1]))
    d += elm.Dot(open=True).at((bx_l - 5, lt[1]))
    d += elm.Label().at((bx_l - 6.5, lt[1])).label("3.3V\n(Zero W)", fontsize=10)

    d += elm.Line().at(lb).to((bx_l - 5, lb[1]))
    d += elm.Dot(open=True).at((bx_l - 5, lb[1]))
    d += elm.Label().at((bx_l - 6.5, lb[1])).label(f"{gpio_label}\n(Zero W)", fontsize=10)
    d += elm.Dot().at((bx_l - 2, lb[1]))
    d += elm.Resistor().at((bx_l - 2, lb[1])).to((bx_l - 2, lb[1] - 2)).label("10kΩ", loc="right", fontsize=9)
    d += elm.Ground().at((bx_l - 2, lb[1] - 2))
    d += elm.Label().at((bx_l - 2, lb[1] - 3.0)).label("Pi GND", fontsize=8)

    # ---- 右 = MB 側(PWR_LED+ から電源を借り、SPEAKER+ 側は MB GND ではなく信号線へ) ----
    # Pin1(右上) ← 1kΩ ← PWR_LED+(MB 5V)
    d += elm.Line().at(rt).to((bx_r + 1, rt[1]))
    d += elm.Resistor().at((bx_r + 1, rt[1])).to((bx_r + 4, rt[1])).label("1kΩ", loc="top", fontsize=9)
    d += elm.Line().at((bx_r + 4, rt[1])).to((bx_r + 5, rt[1]))
    d += elm.Dot(open=True).at((bx_r + 5, rt[1]))
    d += elm.Label().at((bx_r + 6.5, rt[1])).label("PWR_LED+\n(MB, 5V)", fontsize=10)

    # Pin2(右下) → SPEAKER+(MB 信号)
    d += elm.Line().at(rb).to((bx_r + 5, rb[1]))
    d += elm.Dot(open=True).at((bx_r + 5, rb[1]))
    d += elm.Label().at((bx_r + 6.5, rb[1])).label("SPEAKER+\n(MB)", fontsize=10)


with schemdraw.Drawing(file=SVG_PATH, show=False) as d:
    d.config(fontsize=12, unit=2.5)

    # スイッチ系: Pi → MB
    draw_switch_section(d, 0, "GPIO17", "Power Switch", "Physical PWR BTN", "PWR_SW+")
    draw_switch_section(d, -8, "GPIO27", "Reset Switch", "Physical RST BTN", "RST_SW+")

    # 入力系: MB → Pi
    draw_input_section(d, -16, "GPIO22", "Power LED (電源状態)", "PWR_LED+")
    draw_input_section(d, -24, "GPIO23", "HDD LED (ディスクアクセス)", "HDD_LED+")
    draw_speaker_section(d, -32, "GPIO24", "Speaker (ビープ音)")

    d += elm.Label().at((0, -37)).label(
        "全 5 系統を PC817 で完全絶縁。Pi GND と MB GND は基板上・経路上ともに分離。\n"
        "スイッチ系: GPIO=LOW → LED 点灯 → 2 次側導通 → PWR_SW+ が MB GND へ\n"
        "入力系: MB LED 点灯 → 1 次側 LED → 2 次側導通 → Pi 3.3V が GPIO へ → GPIO=HIGH\n"
        "ファーム変更不要(現状の active_high / pull_up 設定のまま動作)",
        fontsize=8,
    )

with open(SVG_PATH, "r") as f:
    svg = f.read()

# viewBox から実際のサイズを読み取り、余白付きで白背景を描画
m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"', svg)
if m:
    vx, vy, vw, vh = map(float, m.groups())
    pad = 20
    bg = f'<rect x="{vx - pad}" y="{vy - pad}" width="{vw + pad * 2}" height="{vh + pad * 2}" fill="white"/>'
else:
    bg = '<rect width="100%" height="100%" fill="white"/>'

svg = svg.replace("<svg ", '<svg style="background-color:white" ', 1)
insert_pos = svg.index(">") + 1
svg = svg[:insert_pos] + bg + svg[insert_pos:]
with open(SVG_PATH, "w") as f:
    f.write(svg)

print("Done: hardware/schematic.svg")
