import schemdraw
import schemdraw.elements as elm

SVG_PATH = "/Users/nya/Documents/Development/pc_power/hardware/schematic.svg"

def draw_switch_section(d, y, gpio_label, section_label, btn_label, header_label):
    """PWR_SW / RST_SW 共通: スイッチ並列接続回路"""
    d += elm.Label().at((0, y)).label(f"[ {section_label} ]", fontsize=13)

    d += (dot := elm.Dot(open=True).at((0, y - 2)))
    d += elm.Label().at((-1.8, y - 2)).label(f"{gpio_label}\n(Zero W)", fontsize=10)

    d += elm.Line().right(3).at(dot.end)
    d += (junc1 := elm.Dot())

    d += elm.Line().up(1.5).at(junc1.center)
    d += elm.Switch().right(3).label(btn_label, loc="top", fontsize=9)
    d += elm.Line().down(1.5)
    d += (junc2 := elm.Dot())

    d += elm.Line().right(2).at(junc1.center)
    d += elm.Line().right(3).at(junc2.center)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 1.5, d.here[1])).label(f"{header_label}\n(MB)", fontsize=10)

    d += elm.Line().down(1.5).at(junc1.center)
    d += elm.Ground()
    d += elm.Line().down(1.5).at(junc2.center)
    d += elm.Ground()


def draw_divider_section(d, y, gpio_label, section_label, header_label):
    """PWR_LED / HDD_LED 共通: 分圧回路"""
    d += elm.Label().at((0, y)).label(f"[ {section_label} ]", fontsize=13)

    d += (dot := elm.Dot(open=True).at((0, y - 2.5)))
    d += elm.Label().at((-1.8, y - 2.5)).label(f"{header_label}\n(MB, 5V)", fontsize=10)

    d += elm.Resistor().right(4).at(dot.end).label("6.8kΩ", loc="top", fontsize=10)
    d += (junc := elm.Dot())

    d += elm.Resistor().down(3).at(junc.center).label("3.3kΩ", loc="right", fontsize=10)
    d += elm.Ground()

    d += elm.Line().right(3).at(junc.center)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 1.5, d.here[1])).label(f"{gpio_label}\n(Zero W)", fontsize=10)

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

    # 5. Speaker
    d += elm.Label().at((0, -28)).label("[ Speaker (ビープ音) ]", fontsize=13)
    d += (spk_dot := elm.Dot(open=True).at((0, -30.5)))
    d += elm.Label().at((-1.8, -30.5)).label("SPEAKER+\n(MB)", fontsize=10)
    d += elm.Line().right(4).at(spk_dot.end)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 1.5, d.here[1])).label("GPIO24\n(Zero W)", fontsize=10)

    # 6. USB Power
    d += elm.Label().at((0, -34)).label("[ 給電 ]", fontsize=13)
    d += (usb_dot := elm.Dot(open=True).at((0, -36)))
    d += elm.Label().at((-2, -36)).label("MB内部USB\nヘッダー(5V)", fontsize=10)
    d += elm.Line().right(4).at(usb_dot.end)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 1.5, d.here[1])).label("PWR端子\n(Zero W)", fontsize=10)

    # Notes
    d += elm.Label().at((0, -39)).label(
        "GPIO17/27: Hi-Z → LOW to press  |  Pulse: ON=500ms / OFF=5s / Reset=500ms\n"
        "GPIO22/23: 分圧 5V→1.65V  |  GPIO24: SPEAKER直結\n"
        "給電: MB内部USBヘッダー (BIOS: USB Standby Power有効)",
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
