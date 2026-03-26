import schemdraw
import schemdraw.elements as elm

SVG_PATH = "/Users/nya/Documents/Development/pc_power/hardware/wiring.svg"

def draw_switch_block(d, y, name, btn_name, gpio_name, mb_name):
    """PWR_SW / RST_SW 中継ブロック"""
    d += elm.Label().at((6, y)).label(name, fontsize=10)

    d += (h1 := elm.Dot(open=True).at((4, y - 1.5)))
    d += (h2 := elm.Dot(open=True).at((8, y - 1.5)))
    d += elm.Line().at(h1.end).to(h2.end)
    d += elm.Label().at((6, y - 1)).label("pin header", fontsize=8)

    # To MB
    d += elm.Line().down(1.5).at(h1.end)
    d += (mb := elm.Dot())
    d += elm.Line().right(7).at(mb.center).color("blue")

    # GND to MB
    d += elm.Line().down(1.5).at(h2.end)
    d += (gnd := elm.Dot())
    d += elm.Line().right(3).at(gnd.center).color("blue")
    d += elm.Line().down(1.5).at(d.here).color("blue")
    d += elm.Line().right(4).at(d.here).color("blue")

    # To Zero W
    d += elm.Line().down(1.5).at(mb.center)
    d += (pi := elm.Dot())

    return pi, gnd


def draw_divider_block(d, y, name, gpio_name, mb_name):
    """PWR_LED / HDD_LED 分圧回路ブロック"""
    d += elm.Label().at((6, y)).label(f"{name} (分圧回路)", fontsize=10)

    d += (inp := elm.Dot().at((4, y - 1.5)))
    d += elm.Resistor().right(4).at(inp.center).label("6.8kΩ", loc="top", fontsize=9)
    d += (mid := elm.Dot())

    d += elm.Resistor().down(2).at(mid.center).label("3.3kΩ", loc="right", fontsize=9)
    d += (gnd := elm.Dot())

    d += elm.Line().right(2).at(mid.center)
    d += (pi := elm.Dot())

    # MB connection
    d += elm.Line().down(1).at(inp.center)
    d += (mb := elm.Dot())
    d += elm.Line().right(7).at(mb.center).color("blue")

    # GND to MB
    d += elm.Line().right(1).at(gnd.center).color("blue")
    d += elm.Line().down(1).at(d.here).color("blue")
    d += elm.Line().right(4).at(d.here).color("blue")

    return pi, gnd


with schemdraw.Drawing(file=SVG_PATH, show=False) as d:
    d.config(fontsize=11, unit=3)

    # Title
    d += elm.Label().at((6, 3)).label("接続図: PCケース ─ 中継基板 ─ マザーボード", fontsize=14)

    # ---- Center: Universal PCB ----
    d += elm.Label().at((6, 0.5)).label("[ ユニバーサル基板 (中継ボード) ]", fontsize=12)

    # PWR_SW
    pwr_pi, _ = draw_switch_block(d, -1, "PWR_SW", "電源ボタン", "GPIO17", "PWR_SW")

    # RST_SW
    rst_pi, _ = draw_switch_block(d, -7.5, "RST_SW", "リセットボタン", "GPIO27", "RST_SW")

    # PWR_LED
    pled_pi, _ = draw_divider_block(d, -14, "PWR_LED", "GPIO22", "PWR_LED")

    # HDD_LED
    hled_pi, _ = draw_divider_block(d, -21, "HDD_LED", "GPIO23", "HDD_LED")

    # SPEAKER (直結)
    d += elm.Label().at((6, -28)).label("SPEAKER", fontsize=10)
    d += (spk_h1 := elm.Dot(open=True).at((4, -29.5)))
    d += (spk_h2 := elm.Dot(open=True).at((8, -29.5)))
    d += elm.Line().at(spk_h1.end).to(spk_h2.end)
    d += elm.Label().at((6, -29)).label("pin header", fontsize=8)

    d += elm.Line().down(1.5).at(spk_h1.end)
    d += (spk_mb := elm.Dot())
    d += elm.Line().right(7).at(spk_mb.center).color("blue")

    d += elm.Line().down(1.5).at(spk_h2.end)
    d += (spk_gnd := elm.Dot())
    d += elm.Line().right(3).at(spk_gnd.center).color("blue")
    d += elm.Line().down(1.5).at(d.here).color("blue")
    d += elm.Line().right(4).at(d.here).color("blue")

    d += elm.Line().down(1.5).at(spk_mb.center)
    spk_pi = elm.Dot()
    d += spk_pi

    # ---- Left: PC Case ----
    d += elm.Label().at((-3, 0.5)).label("[ PCケース ]", fontsize=12)

    d += elm.Switch().at((-5, -2.5)).right(3).label("電源ボタン", loc="top", fontsize=9)
    d += elm.Line().right(1)
    d += elm.Label().at((0.5, -2.5)).label("→", fontsize=12)

    d += elm.Switch().at((-5, -9)).right(3).label("リセットボタン", loc="top", fontsize=9)
    d += elm.Line().right(1)
    d += elm.Label().at((0.5, -9)).label("→", fontsize=12)

    d += elm.Label().at((-3, -15)).label("(LED)", fontsize=9)
    d += elm.Label().at((-3, -22)).label("(LED)", fontsize=9)
    d += elm.Label().at((-3, -29.5)).label("(ブザー)", fontsize=9)

    # ---- Right: Motherboard ----
    d += elm.Label().at((15, 0.5)).label("[ マザーボード ]", fontsize=12)

    for y_pos, name in [(-3.5, "PWR_SW"), (-10, "RST_SW"), (-16.5, "PWR_LED"),
                         (-23.5, "HDD_LED"), (-31, "SPEAKER")]:
        d += elm.Label().at((14.5, y_pos)).label("←", fontsize=12)
        d += elm.Line().right(3).at((15, y_pos - 0.5))
        d += elm.Dot(open=True)
        d += elm.Label().at((19.5, y_pos - 0.5)).label(name, fontsize=10)

    # ---- Bottom: Zero W ----
    d += elm.Label().at((6, -35.5)).label("[ Raspberry Pi Zero W ]", fontsize=12)

    # GPIO lines from PCB to Zero W
    d += elm.Line().down(3).at(pwr_pi.center).color("green")
    d += elm.Label().at((4, -37)).label("↓ GPIO17", fontsize=9)

    d += elm.Line().down(9).at(rst_pi.center).color("green")
    d += elm.Label().at((4, -37.8)).label("↓ GPIO27", fontsize=9)

    d += elm.Line().down(4).at(pled_pi.center).color("green")
    d += elm.Label().at((10, -37)).label("↓ GPIO22", fontsize=9)

    d += elm.Line().down(4).at(hled_pi.center).color("green")
    d += elm.Label().at((10, -37.8)).label("↓ GPIO23", fontsize=9)

    d += elm.Line().down(2).at(spk_pi.center).color("green")
    d += elm.Label().at((4, -38.6)).label("↓ GPIO24", fontsize=9)

    d += elm.Label().at((8, -37.8)).label("↓ GND", fontsize=9)

    d += elm.Label().at((6, -39.5)).label("MB内部USBヘッダー → PWR端子 (常時給電)", fontsize=9)

    # Legend
    d += elm.Label().at((6, -41.5)).label(
        "青線 = デュポンケーブル (MB接続)    緑線 = デュポンケーブル (Zero W接続)",
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
