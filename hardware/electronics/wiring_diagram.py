"""Generates hardware/electronics/wiring.svg — point-to-point wiring of OpenPocket v0 (slim, modules).

Pure-Python SVG (no dependencies). Run: python wiring_diagram.py
wiring.png is a 1:1 raster of the SVG (e.g. headless Chrome: --screenshot --window-size=1300,980).

Revision 19.10.2026 (electronics review): button on D4/GPIO5 (RTC GPIO, deep-sleep wake),
motor CTRL on D7/GPIO44 with a 10 kΩ base-emitter pull-down, motor+ on BAT+, 33 Ω on BCLK,
100 kΩ DOUT pull-down, microSD pull-ups and decoupling, 100 nF on the VBAT divider, junction dots.
"""
import os

W, H = 1300, 980
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiring.svg")

# Net colours (every net its own colour; BAT+ is dashed so it is not mistaken for 3V3)
C = {
    "3V3": "#d62728", "GND": "#111111", "BCLK": "#1f77b4", "LRCL": "#2ca02c",
    "DOUT": "#9467bd", "BTN": "#ff7f0e", "LED": "#e377c2", "MOT": "#8c564b",
    "BAT+": "#d62728", "BAT-": "#111111", "VBAT": "#ad494a",
    "SCK": "#17becf", "MISO": "#7f7f7f", "MOSI": "#bcbd22", "CS": "#e7ba52",
}
DASH = {"BAT+": "7,4", "BAT-": "7,4"}
PART = "#333333"   # passive parts are drawn in dark grey, wires in their net colour

# XIAO ESP32S3 pin rows as seen from the TOP with USB-C pointing UP. All 11 GPIO are used.
LEFT = ["D0 / GPIO1", "D1 / GPIO2", "D2 / GPIO3", "D3 / GPIO4", "D4 / GPIO5", "D5 / GPIO6", "D6 / GPIO43"]
RIGHT = ["5V", "GND", "3V3", "D10 / GPIO9", "D9 / GPIO8", "D8 / GPIO7", "D7 / GPIO44"]

svg = []
add = svg.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif" font-size="13">')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
add('<text x="20" y="30" font-size="20" font-weight="bold">OpenPocket v0 — wiring (modules, point-to-point, 30 AWG silicone wire)</text>')
add('<text x="20" y="50" fill="#444">All logic is 3.3 V. microSD over SPI. Battery pads are on the UNDERSIDE of the XIAO. Haptic motor and VBAT sense are optional.</text>')
add('<text x="20" y="68" fill="#444">A dot marks a connection; wires that cross without a dot are not connected. ⏚ = short wire to GND (XIAO GND pad or the nearest GND splice).</text>')


def box(x, y, w, h, title, fill="#f4f4f4"):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="#333" stroke-width="1.5"/>')
    add(f'<text x="{x + w / 2}" y="{y + 20}" text-anchor="middle" font-weight="bold">{title}</text>')


def pin(x, y, label, side, inside=False, dy=4):
    add(f'<circle cx="{x}" cy="{y}" r="4" fill="#fff" stroke="#333"/>')
    if inside:
        side = "R" if side == "L" else "L"
    anchor = "end" if side == "L" else "start"
    dx = -8 if side == "L" else 8
    add(f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anchor}" font-size="12">{label}</text>')


def wire(pts, net):
    d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
    dash = f' stroke-dasharray="{DASH[net]}"' if net in DASH else ""
    add(f'<path d="{d}" fill="none" stroke="{C[net]}" stroke-width="2.2"{dash}/>')


def line(x1, y1, x2, y2, color=PART, w=1.5):
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"/>')


def dot(x, y, net=None):
    add(f'<circle cx="{x}" cy="{y}" r="3.6" fill="{C[net] if net else PART}"/>')


def text(x, y, s, size=11, fill="#555", anchor="start", weight=None):
    wt = f' font-weight="{weight}"' if weight else ""
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{wt}>{s}</text>')


def res(x1, y1, x2, y2, label=None, lx=0, ly=0, anchor="start"):
    """Zigzag resistor between two points on a horizontal or vertical line."""
    n, a = 6, 4.5
    pts = [(x1, y1)]
    for i in range(n):
        t = (i + 0.5) / n
        s = a if i % 2 == 0 else -a
        if y1 == y2:
            pts.append((x1 + (x2 - x1) * t, y1 + s))
        else:
            pts.append((x1 + s, y1 + (y2 - y1) * t))
    pts.append((x2, y2))
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    add(f'<path d="{d}" fill="none" stroke="{PART}" stroke-width="1.5"/>')
    if label:
        text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, 10, PART, anchor)


def cap(x, y1, y2, label=None, lx=8, anchor="start"):
    """Vertical capacitor between y1 (top) and y2 (bottom): plates in the middle."""
    m = (y1 + y2) / 2
    line(x, y1, x, m - 3)
    line(x, m + 3, x, y2)
    line(x - 8, m - 3, x + 8, m - 3, PART, 2.2)
    line(x - 8, m + 3, x + 8, m + 3, PART, 2.2)
    if label:
        text(x + lx, m + 4, label, 10, PART, anchor)


def gnd(x, y):
    line(x, y - 4, x, y)
    line(x - 7, y, x + 7, y, PART, 1.6)
    line(x - 4.5, y + 3.5, x + 4.5, y + 3.5, PART, 1.6)
    line(x - 2, y + 7, x + 2, y + 7, PART, 1.6)


# ---- XIAO in the middle
XX, XY, XW, XH = 560, 140, 260, 270
box(XX, XY, XW, XH, "Seeed XIAO ESP32S3 (top view, USB-C ↑)", "#e8f3e8")
add(f'<rect x="{XX + XW / 2 - 22}" y="{XY - 10}" width="44" height="14" rx="3" fill="#bbb" stroke="#333"/>')
text(XX + XW / 2, XY + 1, "USB-C", 9, "#111", "middle")
lp = {}
rp = {}
for i, name in enumerate(LEFT):
    y = XY + 50 + i * 30
    pin(XX, y, name, "L", inside=True)
    lp[name.split(" ")[0]] = (XX, y)
for i, name in enumerate(RIGHT):
    y = XY + 50 + i * 30
    pin(XX + XW, y, name, "R", inside=True)
    rp[name.split(" ")[0]] = (XX + XW, y)
text(XX + 8, XY + XH + 17, "Underside pads: BAT+ away from USB, BAT− nearest USB", 10)
batp, batn = (XX + 90, XY + XH - 14), (XX + 170, XY + XH - 14)
pin(*batp, "BAT+", "L")
pin(*batn, "BAT−", "R")

# ---- Mic 1 / Mic 2 (left)
MIC_PINS = ["3V", "GND", "BCLK", "DOUT", "LRCL"]
box(40, 100, 230, 150, "Mic 1 — Adafruit 3421 (SPH0645)", "#e8eaf6")
m1 = {}
for i, n in enumerate(MIC_PINS):
    y = 130 + i * 22
    pin(270, y, n, "L")
    m1[n] = (270, y)
text(52, 240, "SEL bridged to GND on the board = LEFT")
box(40, 300, 230, 150, "Mic 2 — Adafruit 3421 (SPH0645)", "#e8eaf6")
m2 = {}
for i, n in enumerate(MIC_PINS):
    y = 330 + i * 22
    pin(270, y, n, "L")
    m2[n] = (270, y)
text(52, 440, "SEL bridged to 3V on the board = RIGHT")
text(40, 270, "Shared I2S bus: each mic drives DOUT only", 11, C["DOUT"], weight="bold")
text(40, 286, "in its WS half, high-Z otherwise.", 11, C["DOUT"], weight="bold")

# ---- microSD breakout (right top), pins in the physical header order
box(950, 60, 310, 250, "microSD — SparkFun BOB-00544 (SPI)", "#e3f2fd")
sd = {}
for i, n in enumerate(["CS", "DI (MOSI)", "VCC (3V3)", "SCK", "GND", "DO (MISO)", "CD (unused)"]):
    y = 96 + i * 24
    pin(950, y, n, "R")
    sd[n.split(" ")[0]] = (950, y)
# parts soldered at the breakout pads (net labels)
text(1062, 111, "VCC", 10, C["3V3"])
line(1060, 116, 1240, 116, C["3V3"], 2)
for x, lab in zip((1100, 1140, 1180, 1220), ("CS", "DO", "DAT1", "DAT2")):
    dot(x, 116, "3V3")
    line(x, 116, x, 122)
    res(x, 122, x, 158)
    line(x, 158, x, 166)
    text(x, 178, lab, 10, PART, "middle")
text(1160, 194, "4 × 10 kΩ pull-ups to VCC", 10, PART, "middle")
text(1062, 213, "VCC", 10, C["3V3"])
line(1060, 218, 1200, 218, C["3V3"], 2)
for x, lab in ((1110, "10 µF"), (1190, "100 nF")):
    dot(x, 218, "3V3")
    cap(x, 218, 254, lab, 12)
    gnd(x, 262)
text(1155, 296, "soldered at the breakout pads", 10, "#555", "middle")
text(950, 326, "DAT1 = socket pin 8, DAT2 = socket pin 1 (no header pin). CD unused.", 10)

# ---- Button
box(950, 335, 310, 90, "Side button — 6x6 tactile (B3F-1022)", "#fff3e0")
pin(950, 375, "contact A", "R"); pin(950, 398, "contact B (check with meter)", "R")
text(962, 418, "pull-up (RTC), active LOW; wakes from deep sleep (ext0)")

# ---- NeoPixel
box(950, 440, 310, 90, "Status LED — NeoPixel Mini Button (1612)", "#fce4ec")
pin(950, 470, "+ (3V3)", "R"); pin(950, 492, "− (GND)", "R"); pin(950, 514, "DI", "R")

# ---- Motor + driver (optional), drawn as a schematic
box(950, 545, 310, 280, "Haptic (optional) — coin motor + driver", "#efebe9")
pin(950, 580, "BAT+", "R", dy=16)
pin(950, 702, "CTRL", "R", dy=-7)
pin(950, 750, "GND (own wire)", "R", dy=-7)
line(954, 580, 1240, 580, C["BAT+"], 2)              # BAT+ rail at the motor
for x in (1080, 1120, 1190):
    dot(x, 580, "BAT+")
line(1080, 580, 1080, 606)                          # motor
add('<circle cx="1080" cy="620" r="14" fill="#fff" stroke="#333" stroke-width="1.5"/>')
text(1080, 624, "M", 12, PART, "middle", "bold")
line(1080, 634, 1080, 660)
cap(1120, 580, 660, "100 nF", 11)                    # across the motor terminals
line(1190, 580, 1190, 608)                          # flyback diode, cathode to BAT+
add('<polygon points="1183,632 1197,632 1190,610" fill="#fff" stroke="#333" stroke-width="1.5"/>')
line(1182, 610, 1198, 610, PART, 2)
line(1190, 632, 1190, 660)
text(1200, 626, "D1", 10, PART)
line(1080, 660, 1190, 660)                          # motor− / collector node
dot(1120, 660); dot(1140, 660)
line(1140, 660, 1140, 684)                          # Q1 (NPN)
add('<circle cx="1136" cy="702" r="19" fill="none" stroke="#333" stroke-width="1.2"/>')
line(1128, 690, 1128, 714, PART, 2.2)
line(1128, 696, 1140, 684)
line(1128, 708, 1140, 720)
add('<polygon points="1140,720 1131,717 1136,712" fill="#333"/>')
text(1160, 706, "Q1 PN2222A", 10, PART)
line(954, 702, 1010, 702)                           # CTRL → 470 Ω → base
res(1010, 702, 1056, 702, "470 Ω", 0, -9, "middle")
line(1056, 702, 1128, 702)
dot(1090, 702)
line(1090, 702, 1090, 710)                          # 10 kΩ base-emitter pull-down
res(1090, 710, 1090, 740, "10 kΩ", -9, 4, "end")
line(1090, 740, 1090, 750)
line(1140, 720, 1140, 750)
line(954, 750, 1240, 750)                           # emitter / GND node
dot(1090, 750); dot(1140, 750)
line(1240, 580, 1240, 750)                          # 10 µF bulk, BAT+ to GND at the motor
cap(1240, 600, 640)
text(1234, 672, "10 µF", 10, PART, "end")
text(962, 780, "Motor+ and D1 cathode to BAT+, not 3V3.")
text(962, 796, "Emitter returns on its own GND wire to the XIAO.")
text(962, 812, "10 kΩ B–E keeps Q1 off while the ESP32 boots.")

# ---- VBAT sense divider (optional), drawn as a schematic
box(40, 480, 330, 180, "VBAT sense (optional)", "#fbe9e7")
pin(370, 520, "BAT+", "L", inside=True, dy=-7)
pin(370, 566, "D0", "L", inside=True, dy=-7)
line(366, 520, 120, 520, C["BAT+"], 2)
line(120, 520, 120, 528)
res(120, 528, 120, 560, "220 kΩ", 10, 4)
line(120, 560, 120, 572)
line(366, 566, 120, 566, C["VBAT"], 2)
dot(120, 566, "VBAT"); dot(220, 566, "VBAT")
res(120, 572, 120, 604, "220 kΩ", 10, 4)
line(120, 604, 120, 612)
gnd(120, 616)
cap(220, 566, 604, "100 nF", 12)
gnd(220, 612)
text(52, 645, "0–2.1 V on D0: ADC 12 dB attenuation + calibration.")

# ---- Battery and antenna (bottom centre)
box(480, 760, 420, 100, "LiPo 403040, 3.7 V 500 mAh, 4 mm, with PCM", "#fffde7")
pin(560, 760, "RED (+)", "L"); pin(820, 760, "BLACK (−)", "R")
text(495, 810, "Charged by the XIAO (100 mA, ~5 h). Solder one lead at a time;")
text(495, 827, "tape the other. Cover pads with Kapton after soldering.")
text(495, 848, "BAT+ also feeds the motor and the VBAT divider (dashed).", 11, "#b00")
box(480, 880, 420, 70, "2.4 GHz FPC antenna (supplied with the XIAO)", "#f0f0f0")
text(495, 922, "U.FL onto the XIAO; stick the antenna under the RF window insert,")
text(495, 938, "centred at (−31.5, −5.5), long side along Y. Never under solid metal.")

# ---- wires: mics (bus verticals: GND 365, 3V3 380, DOUT 410, LRCL 425, BCLK 440)
y3 = rp["3V3"][1]; yg = rp["GND"][1]
wire([rp["3V3"], (860, y3), (860, 115), (380, 115), (380, m1["3V"][1]), m1["3V"]], "3V3")
wire([(380, m1["3V"][1]), (380, m2["3V"][1]), m2["3V"]], "3V3")
dot(860, y3, "3V3"); dot(860, 115, "3V3"); dot(380, m1["3V"][1], "3V3")
wire([rp["GND"], (875, yg), (875, 100), (365, 100), (365, m1["GND"][1]), m1["GND"]], "GND")
wire([(365, m1["GND"][1]), (365, m2["GND"][1]), m2["GND"]], "GND")
dot(875, 100, "GND"); dot(365, m1["GND"][1], "GND")
# BCLK: 33 Ω series resistor right at the XIAO pin
wire([lp["D1"], (510, lp["D1"][1])], "BCLK")
res(510, lp["D1"][1], 475, lp["D1"][1], "33 Ω", 0, -9, "middle")
wire([(475, lp["D1"][1]), (440, lp["D1"][1]), (440, m1["BCLK"][1]), m1["BCLK"]], "BCLK")
wire([(440, m1["BCLK"][1]), (440, m2["BCLK"][1]), m2["BCLK"]], "BCLK")
dot(440, lp["D1"][1], "BCLK"); dot(440, m1["BCLK"][1], "BCLK")
wire([lp["D2"], (425, lp["D2"][1]), (425, m1["LRCL"][1]), m1["LRCL"]], "LRCL")
wire([(425, m1["LRCL"][1]), (425, m2["LRCL"][1]), m2["LRCL"]], "LRCL")
dot(425, lp["D2"][1], "LRCL"); dot(425, m1["LRCL"][1], "LRCL")
# DOUT: 100 kΩ pull-down right at the XIAO pin
wire([lp["D3"], (410, lp["D3"][1]), (410, m1["DOUT"][1]), m1["DOUT"]], "DOUT")
wire([(410, m1["DOUT"][1]), (410, m2["DOUT"][1]), m2["DOUT"]], "DOUT")
dot(410, lp["D3"][1], "DOUT"); dot(410, m1["DOUT"][1], "DOUT")
dot(495, lp["D3"][1], "DOUT")
line(495, lp["D3"][1], 495, lp["D3"][1] + 8)
res(495, lp["D3"][1] + 8, 495, lp["D3"][1] + 38, "100 kΩ", -8, 4, "end")
gnd(495, lp["D3"][1] + 46)
for (n, net, lab) in (("3V", "3V3", "3V3"), ("GND", "GND", "GND"), ("BCLK", "BCLK", "BCLK"),
                      ("DOUT", "DOUT", "DOUT"), ("LRCL", "LRCL", "LRCL / WS")):
    text(282, m1[n][1] - 4, lab, 10, C[net])

# ---- wires: 3V3 and GND risers on the right (3V3 at x 920, GND at x 905)
wire([(860, 115), (920, 115), (920, 470), (950, 470)], "3V3")
wire([(920, sd["VCC"][1]), sd["VCC"]], "3V3")
dot(920, sd["VCC"][1], "3V3")
wire([(875, 100), (905, 100), (905, 750), (950, 750)], "GND")
for y in (sd["GND"][1], 398, 492):
    wire([(905, y), (950, y)], "GND")
    dot(905, y, "GND")
# ---- wires: microSD SPI
wire([rp["D10"], (840, rp["D10"][1]), (840, sd["DI"][1]), sd["DI"]], "MOSI")
wire([rp["D8"], (850, rp["D8"][1]), (850, sd["SCK"][1]), sd["SCK"]], "SCK")
wire([rp["D9"], (890, rp["D9"][1]), (890, sd["DO"][1]), sd["DO"]], "MISO")
wire([lp["D5"], (532, lp["D5"][1]), (532, 85), (935, 85), (935, sd["CS"][1]), sd["CS"]], "CS")
# ---- wires: button (D4 / GPIO5, RTC GPIO), LED (D6), motor CTRL (D7 / GPIO44)
wire([lp["D4"], (542, lp["D4"][1]), (542, 460), (886, 460), (886, 375), (950, 375)], "BTN")
wire([lp["D6"], (552, lp["D6"][1]), (552, 445), (878, 445), (878, 514), (950, 514)], "LED")
wire([rp["D7"], (895, rp["D7"][1]), (895, 702), (950, 702)], "MOT")
# ---- wires: battery, BAT+ branches to the divider and the motor, VBAT sense to D0
wire([batp, (batp[0], 735), (560, 735), (560, 760)], "BAT+")
wire([batn, (batn[0], 748), (820, 748), (820, 760)], "BAT-")
wire([(batp[0], 520), (370, 520)], "BAT+")
wire([(batp[0], 580), (950, 580)], "BAT+")
dot(batp[0], 520, "BAT+"); dot(batp[0], 580, "BAT+")
wire([lp["D0"], (520, lp["D0"][1]), (520, 566), (370, 566)], "VBAT")

# ---- pin table
text(40, 690, "Pin map (XIAO ESP32S3, all 11 GPIO used)", 13, "#111", weight="bold")
rows = [("D0 / GPIO1", "VBAT sense, 2 × 220 kΩ + 100 nF (optional)"),
        ("D1 / GPIO2", "I2S BCLK (both mics), 33 Ω at the pin"),
        ("D2 / GPIO3", "I2S LRCL / WS (both mics)"),
        ("D3 / GPIO4", "I2S DOUT (both mics), 100 kΩ to GND"),
        ("D4 / GPIO5", "Button to GND, pull-up, deep-sleep wake"),
        ("D5 / GPIO6", "microSD CS (10 kΩ pull-up)"),
        ("D6 / GPIO43", "NeoPixel data (= U0TXD, see firmware)"),
        ("D7 / GPIO44", "Haptic driver CTRL (optional)"),
        ("D8 / GPIO7", "microSD SCK"),
        ("D9 / GPIO8", "microSD DO / MISO (10 kΩ pull-up)"),
        ("D10 / GPIO9", "microSD DI / MOSI")]
for i, (a, b) in enumerate(rows):
    y = 712 + i * 18
    add(f'<text x="40" y="{y}" font-size="12" font-family="Menlo, monospace">{a}</text>')
    add(f'<text x="160" y="{y}" font-size="12">{b}</text>')

add('</svg>')
open(OUT, "w").write("\n".join(svg))
print("wrote", OUT)
