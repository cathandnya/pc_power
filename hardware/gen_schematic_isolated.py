import schemdraw
import schemdraw.elements as elm

SVG_PATH = "/Users/nya/Documents/Development/pc_power/hardware/schematic_isolated.svg"


def draw_switch_section_isolated(d, cy, gpio_label, section_label, header_label):
    """PC817 を 4 ピンの箱として描画。座標は全て絶対指定。"""

    # 箱の中心を (0, cy) に置く
    bx_l, bx_r = -1.5, 1.5
    bx_t, bx_b = cy + 1, cy - 1

    # セクションタイトル
    d += elm.Label().at((0, cy + 2.5)).label(f"[ {section_label} ]", fontsize=13)

    # 箱(Line 4 本で描く)
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

    # Pin4 → PWR_SW+ / RST_SW+
    d += elm.Line().at(pin4).to((bx_r + 5, pin4[1]))
    d += elm.Dot(open=True).at((bx_r + 5, pin4[1]))
    d += elm.Label().at((bx_r + 6.5, pin4[1])).label(f"{header_label}\n(MB)", fontsize=10)

    # Pin3 → MB GND(右に少し出てから下)
    d += elm.Line().at(pin3).to((bx_r + 1, pin3[1]))
    d += elm.Line().at((bx_r + 1, pin3[1])).to((bx_r + 1, pin3[1] - 1.2))
    d += elm.Ground().at((bx_r + 1, pin3[1] - 1.2)).label("MB GND", loc="bottom", fontsize=8)


with schemdraw.Drawing(file=SVG_PATH, show=False) as d:
    d.config(fontsize=12, unit=2.5)

    draw_switch_section_isolated(d, 0, "GPIO17", "Power Switch", "PWR_SW+")
    draw_switch_section_isolated(d, -7, "GPIO27", "Reset Switch", "RST_SW+")

    d += elm.Label().at((0, -12)).label(
        "PC817 で Pi GND と MB GND を完全分離\n"
        "GPIO=INPUT 待機 / LOW 出力で LED 点灯 → 2 次側導通 → PWR_SW+ が MB GND へ\n"
        "現状ファームそのまま使用可(コード変更不要)",
        fontsize=8,
    )

with open(SVG_PATH, "r") as f:
    svg = f.read()
svg = svg.replace("<svg ", '<svg style="background-color:white" ', 1)
insert_pos = svg.index(">") + 1
svg = svg[:insert_pos] + '<rect width="100%" height="100%" fill="white"/>' + svg[insert_pos:]
with open(SVG_PATH, "w") as f:
    f.write(svg)

print("Done: hardware/schematic_isolated.svg")
