import schemdraw
import schemdraw.elements as elm

SVG_PATH = "/Users/nya/Documents/Development/pc_power/hardware/schematic.svg"

# Layout: Left = Zero W, Right = Motherboard

def draw_switch_section(d, cy, gpio_label, section_label, btn_label, header_label):
    """PWR_SW / RST_SW: PC817 で絶縁。Pi GND と MB GND を完全分離。
    物理ボタンも MB GND 側に接続して絶縁を維持。"""
    # 箱の中心を (0, cy) に置く
    bx_l, bx_r = -1.5, 1.5
    bx_t, bx_b = cy + 1, cy - 1

    d += elm.Label().at((0, cy + 2.5)).label(f"[ {section_label} ]", fontsize=13)

    # PC817 の箱(Line 4 本)
    d += elm.Line().at((bx_l, bx_t)).to((bx_r, bx_t))
    d += elm.Line().at((bx_r, bx_t)).to((bx_r, bx_b))
    d += elm.Line().at((bx_r, bx_b)).to((bx_l, bx_b))
    d += elm.Line().at((bx_l, bx_b)).to((bx_l, bx_t))
    d += elm.Label().at((0, cy)).label("PC817", fontsize=10)

    # ピン座標
    pin1 = (bx_l, cy + 0.5)
    pin2 = (bx_l, cy - 0.5)
    pin3 = (bx_r, cy - 0.5)
    pin4 = (bx_r, cy + 0.5)

    # ピン番号
    d += elm.Label().at((bx_l + 0.3, cy + 0.5)).label("1", fontsize=7, color="gray")
    d += elm.Label().at((bx_l + 0.3, cy - 0.5)).label("2", fontsize=7, color="gray")
    d += elm.Label().at((bx_r - 0.3, cy - 0.5)).label("3", fontsize=7, color="gray")
    d += elm.Label().at((bx_r - 0.3, cy + 0.5)).label("4", fontsize=7, color="gray")

    # Pin1 ← 330Ω ← 3.3V
    d += elm.Line().at(pin1).to((bx_l - 1, pin1[1]))
    d += elm.Resistor().at((bx_l - 1, pin1[1])).to((bx_l - 4, pin1[1])).label("330Ω", loc="top", fontsize=9)
    d += elm.Line().at((bx_l - 4, pin1[1])).to((bx_l - 5, pin1[1]))
    d += elm.Dot(open=True).at((bx_l - 5, pin1[1]))
    d += elm.Label().at((bx_l - 6.5, pin1[1])).label("3.3V\n(Zero W)", fontsize=10)

    # Pin2 ← GPIO
    d += elm.Line().at(pin2).to((bx_l - 5, pin2[1]))
    d += elm.Dot(open=True).at((bx_l - 5, pin2[1]))
    d += elm.Label().at((bx_l - 6.5, pin2[1])).label(f"{gpio_label}\n(Zero W)", fontsize=10)

    # Pin4 → header (PWR_SW+ / RST_SW+)、途中で物理ボタン分岐
    d += elm.Line().at(pin4).to((bx_r + 5, pin4[1]))
    d += elm.Dot(open=True).at((bx_r + 5, pin4[1]))
    d += elm.Label().at((bx_r + 6.5, pin4[1])).label(f"{header_label}\n(MB)", fontsize=10)
    d += (sig_junc := elm.Dot().at((bx_r + 3, pin4[1])))
    d += elm.Label().at((bx_r + 3, pin4[1] + 0.4)).label(btn_label, fontsize=9)

    # 物理ボタン: junction から少し下ろしてからスイッチ
    btn_x = bx_r + 3
    d += elm.Line().at(sig_junc.center).to((btn_x, pin4[1] - 0.5))
    d += elm.Switch().at((btn_x, pin4[1] - 0.5)).to((btn_x, pin4[1] - 2.5))

    # Pin3 は別ルートで下へ(ボタンと重ならないよう箱のすぐ下で右へ)
    pin3_down_x = bx_r + 1.5
    d += elm.Line().at(pin3).to((pin3_down_x, pin3[1]))
    d += elm.Line().at((pin3_down_x, pin3[1])).to((pin3_down_x, pin4[1] - 3))

    # GND 合流点
    d += elm.Line().at((pin3_down_x, pin4[1] - 3)).to((btn_x, pin4[1] - 3))
    d += elm.Line().at((btn_x, pin4[1] - 2.5)).to((btn_x, pin4[1] - 3))
    d += elm.Ground().at((btn_x, pin4[1] - 3)).label("MB GND", loc="bottom", fontsize=8)


def draw_divider_section(d, y, gpio_label, section_label, header_label):
    """PWR_LED / HDD_LED: voltage divider"""
    d += elm.Label().at((0, y)).label(f"[ {section_label} ]", fontsize=13)

    # Left: Zero W GPIO
    d += (gpio_dot := elm.Dot(open=True).at((0, y - 2.5)))
    d += elm.Label().at((-1.8, y - 2.5)).label(f"{gpio_label}\n(Zero W)", fontsize=10)

    d += elm.Line().right(2).at(gpio_dot.end)
    d += (junc := elm.Dot())

    # Divider: R2 to GND
    d += elm.Resistor().down(3).at(junc.center).label("3.3kΩ", loc="right", fontsize=10)
    d += elm.Ground()

    # R1 to MB
    d += elm.Resistor().right(4).at(junc.center).label("6.8kΩ", loc="top", fontsize=10)

    # Right: Motherboard header
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 1.8, d.here[1])).label(f"{header_label}\n(MB, 5V)", fontsize=10)

    d += elm.Label().at((junc.center[0], junc.center[1] + 0.8)).label("≈1.65V", fontsize=9)


with schemdraw.Drawing(file=SVG_PATH, show=False) as d:
    d.config(fontsize=12, unit=3)

    # 1. Power Switch
    draw_switch_section(d, 0, "GPIO17", "Power Switch", "Physical PWR BTN", "PWR_SW+")

    # 2. Reset Switch
    draw_switch_section(d, -7, "GPIO27", "Reset Switch", "Physical RST BTN", "RST_SW+")

    # 3. Power LED (voltage divider)
    draw_divider_section(d, -14, "GPIO22", "Power LED (電源状態)", "PWR_LED+")

    # 4. HDD LED (voltage divider)
    draw_divider_section(d, -21, "GPIO23", "HDD LED (ディスクアクセス)", "HDD_LED+")

    # 5. Speaker (10kΩ clamp)
    d += elm.Label().at((0, -28)).label("[ Speaker (ビープ音) ]", fontsize=13)
    d += (spk_gpio := elm.Dot(open=True).at((0, -30.5)))
    d += elm.Label().at((-1.8, -30.5)).label("GPIO24\n(Zero W)", fontsize=10)
    d += elm.Resistor().right(4).at(spk_gpio.end).label("10kΩ", loc="top", fontsize=10)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 1.8, d.here[1])).label("SPEAKER+\n(MB)", fontsize=10)

    # Notes
    d += elm.Label().at((0, -34)).label(
        "左 = Raspberry Pi Zero W    右 = マザーボード\n"
        "GPIO17/27: PC817 で絶縁。GPIO=INPUT 待機 / LOW 出力で押下 (コード変更不要)\n"
        "  Pi GND と MB GND は完全分離。物理ボタンも MB GND 側に接続\n"
        "  Pulse: ON=500ms / OFF=5s / Reset=500ms\n"
        "GPIO22/23: 分圧 5V→1.65V (Pi GND)  |  GPIO24: 10kΩクランプ (Pi GND)",
        fontsize=8
    )

# Add white background
with open(SVG_PATH, "r") as f:
    svg = f.read()
svg = svg.replace("<svg ", '<svg style="background-color:white" ', 1)
insert_pos = svg.index(">") + 1
svg = svg[:insert_pos] + '<rect width="100%" height="100%" fill="white"/>' + svg[insert_pos:]
with open(SVG_PATH, "w") as f:
    f.write(svg)

print("Done: hardware/schematic.svg")
