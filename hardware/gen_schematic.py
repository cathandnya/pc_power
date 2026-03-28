import schemdraw
import schemdraw.elements as elm

SVG_PATH = "/Users/nya/Documents/Development/pc_power/hardware/schematic.svg"

# Layout: Left = Zero W, Right = Motherboard

def draw_switch_section(d, y, gpio_label, section_label, btn_label, header_label):
    """PWR_SW / RST_SW: switch parallel circuit"""
    d += elm.Label().at((0, y)).label(f"[ {section_label} ]", fontsize=13)

    # Left: Zero W GPIO
    d += (dot := elm.Dot(open=True).at((0, y - 2)))
    d += elm.Label().at((-1.8, y - 2)).label(f"{gpio_label}\n(Zero W)", fontsize=10)

    d += elm.Line().right(3).at(dot.end)
    d += (junc1 := elm.Dot())

    # Parallel physical button
    d += elm.Line().up(1.5).at(junc1.center)
    d += elm.Switch().right(3).label(btn_label, loc="top", fontsize=9)
    d += elm.Line().down(1.5)
    d += (junc2 := elm.Dot())

    d += elm.Line().right(2).at(junc1.center)
    d += elm.Line().right(3).at(junc2.center)

    # Right: Motherboard header
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 1.8, d.here[1])).label(f"{header_label}\n(MB)", fontsize=10)

    d += elm.Line().down(1.5).at(junc1.center)
    d += elm.Ground()
    d += elm.Line().down(1.5).at(junc2.center)
    d += elm.Ground()


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
        "GPIO17/27: Hi-Z → LOW to press  |  Pulse: ON=500ms / OFF=5s / Reset=500ms\n"
        "GPIO22/23: 分圧 5V→1.65V  |  GPIO24: 10kΩクランプ (5V/3.3V両対応)",
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
