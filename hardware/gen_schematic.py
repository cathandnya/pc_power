import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing(file="/Users/nya/Documents/Development/pc_power/hardware/schematic.svg", show=False) as d:
    d.config(fontsize=12, unit=3)

    # =============================================
    # Power Switch Section
    # =============================================
    # Section label
    d += elm.Label().at((0, 0)).label("[ Power Switch ]", fontsize=13)

    # GP16 label
    d += (gp16_dot := elm.Dot(open=True).at((0, -2)))
    d += elm.Label().at((-1.5, -2)).label("GP16\n(Pico W)", fontsize=10)

    # Wire from GP16 to junction
    d += elm.Line().right(3).at(gp16_dot.end)
    d += (pwr_junc1 := elm.Dot())

    # Physical power button (parallel path - goes up)
    d += elm.Line().up(1.5).at(pwr_junc1.center)
    d += elm.Switch().right(3).label("Physical PWR BTN", loc="top", fontsize=9)
    d += elm.Line().down(1.5)
    d += (pwr_junc2 := elm.Dot())

    # Direct wire (lower path)
    d += elm.Line().right(2).at(pwr_junc1.center)
    junc1_pos = d.here
    d += elm.Line().right(3).at(pwr_junc2.center)

    # MB header label
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 1.5, d.here[1])).label("PWR_SW+\n(MB)", fontsize=10)

    # GND connections
    d += elm.Line().down(1.5).at(pwr_junc1.center)
    d += elm.Ground()

    d += elm.Line().down(1.5).at(pwr_junc2.center)
    d += elm.Ground()

    # =============================================
    # Reset Switch Section
    # =============================================
    d += elm.Label().at((0, -7)).label("[ Reset Switch ]", fontsize=13)

    d += (gp17_dot := elm.Dot(open=True).at((0, -9)))
    d += elm.Label().at((-1.5, -9)).label("GP17\n(Pico W)", fontsize=10)

    d += elm.Line().right(3).at(gp17_dot.end)
    d += (rst_junc1 := elm.Dot())

    d += elm.Line().up(1.5).at(rst_junc1.center)
    d += elm.Switch().right(3).label("Physical RST BTN", loc="top", fontsize=9)
    d += elm.Line().down(1.5)
    d += (rst_junc2 := elm.Dot())

    d += elm.Line().right(2).at(rst_junc1.center)
    d += elm.Line().right(3).at(rst_junc2.center)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 1.5, d.here[1])).label("RST_SW+\n(MB)", fontsize=10)

    d += elm.Line().down(1.5).at(rst_junc1.center)
    d += elm.Ground()

    d += elm.Line().down(1.5).at(rst_junc2.center)
    d += elm.Ground()

    # =============================================
    # Power LED Voltage Divider Section
    # =============================================
    d += elm.Label().at((0, -14)).label("[ Power LED Status Detection ]", fontsize=13)

    # PWR_LED+ from MB
    d += (led_dot := elm.Dot(open=True).at((0, -16.5)))
    d += elm.Label().at((-1.8, -16.5)).label("PWR_LED+\n(MB, 5V)", fontsize=10)

    # R1: 6.8kΩ
    d += elm.Resistor().right(4).at(led_dot.end).label("R1  6.8kΩ", loc="top", fontsize=10)
    d += (div_junc := elm.Dot())

    # R2: 3.3kΩ to GND
    d += elm.Resistor().down(3).at(div_junc.center).label("R2\n3.3kΩ", loc="right", fontsize=10)
    d += elm.Ground()

    # Wire to GP18
    d += elm.Line().right(3).at(div_junc.center)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 1.5, d.here[1])).label("GP18\n(Pico W)", fontsize=10)

    # GP18 voltage annotation
    d += elm.Label().at((div_junc.center[0], div_junc.center[1] + 0.8)).label("≈1.65V", fontsize=9)

    # =============================================
    # USB Power Section
    # =============================================
    d += elm.Label().at((0, -22)).label("[ Pico W Power Supply ]", fontsize=13)

    d += (usb_dot := elm.Dot(open=True).at((0, -24)))
    d += elm.Label().at((-1.8, -24)).label("USB充電器\n(5V)", fontsize=10)
    d += elm.Line().right(4).at(usb_dot.end)
    d += elm.Dot(open=True)
    d += elm.Label().at((d.here[0] + 1.5, d.here[1])).label("VBUS\n(Pico W)", fontsize=10)

    # =============================================
    # Notes
    # =============================================
    d += elm.Label().at((0, -27.5)).label(
        "GP16/GP17: Hi-Z (Pin.IN) → LOW (Pin.OUT) to press\n"
        "Pulse: ON=500ms / OFF=5000ms / Reset=500ms\n"
        "Divider: 5V × 3.3k/(6.8k+3.3k) ≈ 1.65V",
        fontsize=9
    )

# Add white background to SVG
svg_path = "/Users/nya/Documents/Development/pc_power/hardware/schematic.svg"
with open(svg_path, "r") as f:
    svg = f.read()
svg = svg.replace(
    "<svg ",
    '<svg style="background-color:white" ',
    1,
)
# Insert a white rect right after the opening svg tag
insert_pos = svg.index(">") + 1
svg = svg[:insert_pos] + '<rect width="100%" height="100%" fill="white"/>' + svg[insert_pos:]
with open(svg_path, "w") as f:
    f.write(svg)

print("Done: hardware/schematic.svg")
