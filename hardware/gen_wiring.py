import schemdraw
import schemdraw.elements as elm

SVG_PATH = "/Users/nya/Documents/Development/pc_power/hardware/wiring.svg"

# Layout: Left = Zero W (x=-4), Center = Universal PCB (x=4..8), Right = Motherboard (x=15)
# All blue lines end at x=15, all green lines end at x=-4

ZW_X = -4       # Zero W column
PCB_L = 4       # PCB left edge
PCB_R = 8       # PCB right edge
MB_X = 15       # Motherboard column (line endpoint)
MB_LBL = 17     # Motherboard label position


def draw_switch_block(d, y, name):
    """PWR_SW / RST_SW relay block on PCB"""
    d += elm.Label().at((6, y)).label(name, fontsize=10)

    # Pin headers for case button
    d += (h1 := elm.Dot(open=True).at((PCB_L, y - 1.5)))
    d += (h2 := elm.Dot(open=True).at((PCB_R, y - 1.5)))
    d += elm.Line().at(h1.end).to(h2.end)
    d += elm.Label().at((6, y - 1)).label("pin header", fontsize=8)

    # Signal: h1 down to branch point
    d += elm.Line().down(1.5).at(h1.end)
    d += (branch := elm.Dot())

    # Left (green): branch → Zero W
    d += elm.Line().at(branch.center).to((ZW_X, branch.center[1])).color("green")

    # Down from branch, then right (blue): → MB
    d += elm.Line().down(1.5).at(branch.center)
    d += (mb := elm.Dot())
    d += elm.Line().at(mb.center).to((MB_X, mb.center[1])).color("blue")

    # GND: h2 down, then right (blue): → MB
    d += elm.Line().down(3).at(h2.end)
    d += (gnd := elm.Dot())
    d += elm.Line().at(gnd.center).to((MB_X, gnd.center[1])).color("blue")


def draw_divider_block(d, y, name):
    """PWR_LED / HDD_LED divider block on PCB"""
    d += elm.Label().at((6, y)).label(f"{name} (分圧回路)", fontsize=10)

    # Input from MB (blue): MB → PCB right edge
    d += (inp := elm.Dot().at((PCB_R, y - 1.5)))
    d += elm.Line().at(inp.center).to((MB_X, inp.center[1])).color("blue")

    # Divider resistors
    d += elm.Resistor().left(4).at(inp.center).label("6.8kΩ", loc="top", fontsize=9)
    d += (mid := elm.Dot())

    d += elm.Resistor().down(2).at(mid.center).label("3.3kΩ", loc="right", fontsize=9)
    d += (gnd := elm.Dot())

    # GND (blue): → MB
    d += elm.Line().at(gnd.center).to((MB_X, gnd.center[1])).color("blue")

    # Output to Zero W (green): mid → Zero W
    d += elm.Line().at(mid.center).to((ZW_X, mid.center[1])).color("green")


def draw_speaker_block(d, y):
    """SPEAKER block on PCB"""
    d += elm.Label().at((6, y)).label("SPEAKER", fontsize=10)

    d += (h1 := elm.Dot(open=True).at((PCB_L, y - 1.5)))
    d += (h2 := elm.Dot(open=True).at((PCB_R, y - 1.5)))
    d += elm.Line().at(h1.end).to(h2.end)
    d += elm.Label().at((6, y - 1)).label("pin header", fontsize=8)

    # Signal: h1 down, branch left (green) and right (blue)
    d += elm.Line().down(1.5).at(h1.end)
    d += (branch := elm.Dot())

    # Left (green): → Zero W
    d += elm.Line().at(branch.center).to((ZW_X, branch.center[1])).color("green")

    # Right (blue): → MB
    d += elm.Line().at(branch.center).to((MB_X, branch.center[1])).color("blue")

    # GND: h2 down, then right (blue): → MB
    d += elm.Line().down(1.5).at(h2.end)
    d += (gnd := elm.Dot())
    d += elm.Line().at(gnd.center).to((MB_X, gnd.center[1])).color("blue")


with schemdraw.Drawing(file=SVG_PATH, show=False) as d:
    d.config(fontsize=11, unit=3)

    # Title
    d += elm.Label().at((6, 3)).label("接続図: Zero W ─ 中継基板 ─ マザーボード", fontsize=14)

    # Column headers
    d += elm.Label().at((ZW_X, 0.5)).label("[ Zero W ]", fontsize=12)
    d += elm.Label().at((6, 0.5)).label("[ ユニバーサル基板 ]", fontsize=12)
    d += elm.Label().at((MB_LBL, 0.5)).label("[ マザーボード ]", fontsize=12)

    # Blocks
    draw_switch_block(d, -1, "PWR_SW")
    draw_switch_block(d, -8, "RST_SW")
    draw_divider_block(d, -15, "PWR_LED")
    draw_divider_block(d, -22, "HDD_LED")
    draw_speaker_block(d, -29)

    # Left side GPIO labels
    d += elm.Label().at((ZW_X, -3)).label("GPIO17", fontsize=9)
    d += elm.Label().at((ZW_X, -10)).label("GPIO27", fontsize=9)
    d += elm.Label().at((ZW_X, -17)).label("GPIO22", fontsize=9)
    d += elm.Label().at((ZW_X, -24)).label("GPIO23", fontsize=9)
    d += elm.Label().at((ZW_X, -31)).label("GPIO24", fontsize=9)

    # Right side MB header labels
    d += elm.Label().at((MB_LBL, -4.5)).label("PWR_SW", fontsize=9)
    d += elm.Label().at((MB_LBL, -5.5)).label("(+/GND)", fontsize=7)
    d += elm.Label().at((MB_LBL, -11.5)).label("RST_SW", fontsize=9)
    d += elm.Label().at((MB_LBL, -12.5)).label("(+/GND)", fontsize=7)
    d += elm.Label().at((MB_LBL, -16.5)).label("PWR_LED", fontsize=9)
    d += elm.Label().at((MB_LBL, -17.5)).label("(+/GND)", fontsize=7)
    d += elm.Label().at((MB_LBL, -23.5)).label("HDD_LED", fontsize=9)
    d += elm.Label().at((MB_LBL, -24.5)).label("(+/GND)", fontsize=7)
    d += elm.Label().at((MB_LBL, -31)).label("SPEAKER", fontsize=9)
    d += elm.Label().at((MB_LBL, -32)).label("(+/GND)", fontsize=7)

    # Notes
    d += elm.Label().at((6, -36)).label("ケースボタン: ピンヘッダーに差し込み (PWR_SW / RST_SW)", fontsize=8)
    d += elm.Label().at((6, -37.5)).label(
        "緑線 = Zero W接続    青線 = マザーボード接続",
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

print("Done: hardware/wiring.svg")
