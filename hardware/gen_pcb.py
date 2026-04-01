import schemdraw
import schemdraw.elements as elm

SVG_PATH = "/Users/nya/Documents/Development/pc_power/hardware/pcb_layout.svg"

RIGHT_X = 14  # Right column for pin headers


def draw_switch_block(d, y, gpio_name, section_name, case_label):
    """PWR_SW / RST_SW block"""
    d += elm.Label().at((7, y)).label(section_name, fontsize=10).color("#333")

    # Left: GPIO pin header
    d += (gpio := elm.Dot(open=True).at((0, y - 2)))
    d += elm.Label().at((-1.5, y - 2)).label(gpio_name, fontsize=10)

    # Signal wire to junction
    d += elm.Line().right(10).at(gpio.end)
    d += (junc := elm.Dot())

    # Right: MB pin header
    d += elm.Line().right(4).at(junc.center)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 2, d.here[1])).label(f"→ MB {section_name}+", fontsize=9)

    # Up: case button pin header
    d += elm.Line().up(1.5).at(junc.center)
    d += elm.Line().right(4)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 2, d.here[1])).label(f"← {case_label}", fontsize=9)

    # Case button GND pin header + GND symbol
    case_gnd_y = y - 3.5
    d += elm.Dot(open=True).at((RIGHT_X, case_gnd_y))
    d += elm.Label().at((RIGHT_X + 2, case_gnd_y)).label(f"← {case_label} (GND)", fontsize=9)
    d += elm.Line().left(2).at((RIGHT_X, case_gnd_y))
    d += elm.Line().down(1)
    d += elm.Ground()

    # MB GND pin header + GND symbol
    mb_gnd_y = y - 5
    d += elm.Dot(open=True).at((RIGHT_X, mb_gnd_y))
    d += elm.Label().at((RIGHT_X + 2, mb_gnd_y)).label(f"→ MB {section_name} GND", fontsize=9)
    d += elm.Line().left(2).at((RIGHT_X, mb_gnd_y))
    d += elm.Line().down(1)
    d += elm.Ground()


def draw_divider_block(d, y, gpio_name, section_name, r1_name, r2_name):
    """PWR_LED / HDD_LED divider block"""
    d += elm.Label().at((7, y)).label(f"{section_name} (分圧回路)", fontsize=10).color("#333")

    # Left: GPIO pin header
    d += (gpio := elm.Dot(open=True).at((0, y - 2.5)))
    d += elm.Label().at((-1.5, y - 2.5)).label(gpio_name, fontsize=10)

    # Wire to junction
    d += elm.Line().right(3).at(gpio.end)
    d += (junc := elm.Dot())

    # R2 down to GND
    d += elm.Resistor().down(3).at(junc.center).label(f"{r2_name}\n3.3kΩ", loc="right", fontsize=9)
    d += elm.Ground()

    # R1 to MB
    d += elm.Resistor().right(5).at(junc.center).label(f"{r1_name}  6.8kΩ", loc="top", fontsize=9)
    d += elm.Line().right(2)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 2, d.here[1])).label(f"→ MB {section_name}+", fontsize=9)

    # MB GND pin header + GND symbol
    mb_gnd_y = y - 5.5
    d += elm.Dot(open=True).at((RIGHT_X, mb_gnd_y))
    d += elm.Label().at((RIGHT_X + 2, mb_gnd_y)).label(f"→ MB {section_name} GND", fontsize=9)
    d += elm.Line().left(2).at((RIGHT_X, mb_gnd_y))
    d += elm.Line().down(1)
    d += elm.Ground()


with schemdraw.Drawing(file=SVG_PATH, show=False) as d:
    d.config(fontsize=11, unit=3)

    # Title
    d += elm.Label().at((7, 3)).label("ユニバーサル基板 実装図", fontsize=15)
    d += elm.Label().at((7, 2)).label("(左: Zero W側ピンヘッダー  右: MB/ケース側ピンヘッダー)", fontsize=9)

    # ---- J1: Zero W side ----
    d += elm.Label().at((0, 0.5)).label("J1: Zero W側", fontsize=10)

    # 1. PWR_SW
    draw_switch_block(d, 0, "GPIO17", "PWR_SW", "ケース電源BTN")

    # 2. RST_SW
    draw_switch_block(d, -8, "GPIO27", "RST_SW", "ケースRST BTN")

    # 3. PWR_LED
    draw_divider_block(d, -16, "GPIO22", "PWR_LED", "R1", "R2")

    # 4. HDD_LED
    draw_divider_block(d, -24, "GPIO23", "HDD_LED", "R3", "R4")

    # 5. SPEAKER (10kΩ clamp)
    Y = -32
    d += elm.Label().at((7, Y)).label("SPEAKER (10kΩクランプ)", fontsize=10).color("#333")

    d += (g24 := elm.Dot(open=True).at((0, Y - 2)))
    d += elm.Label().at((-1.5, Y - 2)).label("GPIO24", fontsize=10)

    d += elm.Resistor().right(5).at(g24.end).label("R5  10kΩ", loc="top", fontsize=9)
    d += elm.Line().right(5)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 2, d.here[1])).label("→ MB SPEAKER+", fontsize=9)

    # SPEAKER GND
    spk_gnd_y = Y - 3.5
    d += elm.Dot(open=True).at((RIGHT_X, spk_gnd_y))
    d += elm.Label().at((RIGHT_X + 2, spk_gnd_y)).label("→ MB SPEAKER GND", fontsize=9)
    d += elm.Line().left(2).at((RIGHT_X, spk_gnd_y))
    d += elm.Line().down(1)
    d += elm.Ground()

    # GND pin header (Zero W side)
    gnd_y = -37
    d += elm.Dot(open=True).at((0, gnd_y))
    d += elm.Label().at((-1.5, gnd_y)).label("GND", fontsize=10)
    d += elm.Line().right(1).at((0, gnd_y))
    d += elm.Ground()
    d += elm.Label().at((4, gnd_y)).label("← Zero W GND (Pin 14)", fontsize=9)

    # Legend
    d += elm.Label().at((7, -39.5)).label(
        "○ = ピンヘッダー (2.54mm)    ▼ = GND (すべて基板上で共通接続)",
        fontsize=8
    )
    d += elm.Label().at((7, -40.5)).label(
        "R1,R3: 6.8kΩ  R2,R4: 3.3kΩ  R5: 10kΩ  すべて1/4W",
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

print("Done: hardware/pcb_layout.svg")
