"""Generates hardware/electronics/wiring.svg — point-to-point wiring of OpenPocket v0 (slim, modules).

Pure-Python SVG (no dependencies). Run: python wiring_diagram.py
"""
import os

W, H = 1200, 860
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiring.svg")

# Net colours
C = {
    "3V3": "#d62728", "GND": "#111111", "BCLK": "#1f77b4", "LRCL": "#2ca02c",
    "DOUT": "#9467bd", "BTN": "#ff7f0e", "LED": "#e377c2", "MOT": "#8c564b",
    "BAT+": "#d62728", "BAT-": "#111111", "VBAT": "#bcbd22",
    "SCK": "#17becf", "MISO": "#7f7f7f", "MOSI": "#bcbd22", "CS": "#e7ba52",
}

# XIAO ESP32S3 pin rows (as seen from the TOP, USB-C at the right). All 11 GPIO are used.
LEFT = ["D0 / GPIO1", "D1 / GPIO2", "D2 / GPIO3", "D3 / GPIO4", "D4 / GPIO5", "D5 / GPIO6", "D6 / GPIO43"]
RIGHT = ["5V", "GND", "3V3", "D10 / GPIO9", "D9 / GPIO8", "D8 / GPIO7", "D7 / GPIO44"]

svg = []
add = svg.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif" font-size="13">')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
add('<text x="20" y="30" font-size="20" font-weight="bold">OpenPocket v0 — wiring (modules, point-to-point, 30 AWG silicone wire)</text>')
add('<text x="20" y="50" fill="#444">All logic is 3.3 V. Both mics share one I2S bus (BCLK, LRCL, DOUT); mic 1 SEL→GND (left), mic 2 SEL→3V3 (right). microSD over SPI. Battery pads are on the UNDERSIDE of the XIAO.</text>')


def box(x, y, w, h, title, fill="#f4f4f4"):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="#333" stroke-width="1.5"/>')
    add(f'<text x="{x + w / 2}" y="{y + 20}" text-anchor="middle" font-weight="bold">{title}</text>')


def pin(x, y, label, side, inside=False):
    add(f'<circle cx="{x}" cy="{y}" r="4" fill="#fff" stroke="#333"/>')
    if inside:
        side = "R" if side == "L" else "L"
    anchor = "end" if side == "L" else "start"
    dx = -8 if side == "L" else 8
    add(f'<text x="{x + dx}" y="{y + 4}" text-anchor="{anchor}" font-size="12">{label}</text>')


def wire(pts, net, label=None):
    d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
    add(f'<path d="{d}" fill="none" stroke="{C[net]}" stroke-width="2.2"/>')
    if label:
        x, y = pts[-1]
        add(f'<text x="{x + 6}" y="{y - 4}" font-size="11" fill="{C[net]}">{label}</text>')


# ---- XIAO in the middle
XX, XY, XW, XH = 470, 120, 260, 260
box(XX, XY, XW, XH, "Seeed XIAO ESP32S3 (top view, USB-C →)", "#e8f3e8")
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
add(f'<text x="{XX + XW / 2}" y="{XY + XH + 18}" text-anchor="middle" font-size="11" fill="#555">Underside pads: BAT+ away from USB, BAT− nearest USB</text>')
pin(XX + 90, XY + XH - 12, "BAT+", "L")
pin(XX + 170, XY + XH - 12, "BAT−", "R")
batp, batn = (XX + 90, XY + XH - 12), (XX + 170, XY + XH - 12)

# ---- Mic 1 (left top)
box(60, 90, 220, 160, "Mic 1 — Adafruit 3421 (SPH0645)", "#e8eaf6")
m1 = {}
for i, n in enumerate(["3V", "GND", "BCLK", "DOUT", "LRCL", "SEL"]):
    y = 120 + i * 22
    pin(280, y, n, "L")
    m1[n] = (280, y)
add('<text x="70" y="240" font-size="11" fill="#555">SEL → GND = LEFT channel</text>')

# ---- Mic 2 (left bottom)
box(60, 300, 220, 160, "Mic 2 — Adafruit 3421 (SPH0645)", "#e8eaf6")
m2 = {}
for i, n in enumerate(["3V", "GND", "BCLK", "DOUT", "LRCL", "SEL"]):
    y = 330 + i * 22
    pin(280, y, n, "L")
    m2[n] = (280, y)
add('<text x="70" y="450" font-size="11" fill="#555">SEL → 3V = RIGHT channel</text>')

# ---- microSD breakout (right top)
box(880, 90, 260, 160, "microSD — SparkFun BOB-00544 (SPI)", "#e3f2fd")
sd = {}
for i, n in enumerate(["VCC (3V3)", "GND", "CS", "DI (MOSI)", "SCK", "DO (MISO)"]):
    y = 120 + i * 22
    pin(880, y, n, "R")
    sd[n.split(" ")[0]] = (880, y)
add('<text x="895" y="245" font-size="11" fill="#555">CD pin unused. 3.3 V only, no level shifter needed.</text>')

# ---- Button (right middle)
box(880, 270, 260, 80, "Side button — 6x6 tactile (B3F-1022)", "#fff3e0")
pin(880, 305, "pin 1", "R"); pin(880, 330, "pin 2", "R")
add('<text x="1000" y="343" font-size="11" fill="#555">internal pull-up, active LOW</text>')

# ---- NeoPixel (right)
box(880, 370, 260, 90, "Status LED — NeoPixel Mini Button (1612)", "#fce4ec")
pin(880, 400, "+ (3V3)", "R"); pin(880, 422, "− (GND)", "R"); pin(880, 444, "DI", "R")

# ---- Motor + driver (right bottom), optional
box(880, 480, 260, 150, "Haptic (optional) — coin motor + driver", "#efebe9")
pin(880, 510, "3V3", "R"); pin(880, 535, "GND", "R"); pin(880, 560, "CTRL (1 kΩ to base)", "R")
add('<text x="895" y="585" font-size="11" fill="#555">Q1 PN2222A: E→GND, C→motor−, B→1kΩ→CTRL</text>')
add('<text x="895" y="602" font-size="11" fill="#555">motor+ → 3V3; D1 1N4148 across motor (cathode to 3V3)</text>')
add('<text x="895" y="619" font-size="11" fill="#555">100 nF across motor terminals</text>')

# ---- Battery (bottom centre)
box(430, 600, 340, 110, "LiPo 403040, 3.7 V 500 mAh, 4 mm, with PCM", "#fffde7")
pin(520, 600, "RED (+)", "L"); pin(680, 600, "BLACK (−)", "R")
add('<text x="445" y="650" font-size="11" fill="#555">Charged by the XIAO (100 mA, ~5 h). Solder one lead at a time;</text>')
add('<text x="445" y="667" font-size="11" fill="#555">tape the other. Cover pads with Kapton after soldering.</text>')
add('<text x="445" y="690" font-size="11" fill="#b00">Optional VBAT sense: BAT+ → 220 kΩ → D0, D0 → 220 kΩ → GND</text>')

# ---- Antenna note
box(430, 740, 340, 70, "2.4 GHz FPC antenna (supplied with XIAO)", "#f0f0f0")
add('<text x="445" y="785" font-size="11" fill="#555">U.FL plug onto the XIAO connector; stick antenna under the lid at the −X end.</text>')

# ---- wires: mics
y3 = rp["3V3"][1]; yg = rp["GND"][1]
wire([rp["3V3"], (rp["3V3"][0] + 40, y3), (rp["3V3"][0] + 40, XY - 25), (XX - 60, XY - 25), (XX - 60, m1["3V"][1]), m1["3V"]], "3V3")
wire([(XX - 60, m1["3V"][1]), (XX - 60, m2["3V"][1]), m2["3V"]], "3V3")
wire([(XX - 60, m2["3V"][1]), (XX - 60, m2["SEL"][1]), m2["SEL"]], "3V3", "SEL=3V3 (R)")
wire([rp["GND"], (rp["GND"][0] + 55, yg), (rp["GND"][0] + 55, XY - 40), (XX - 75, XY - 40), (XX - 75, m1["GND"][1]), m1["GND"]], "GND")
wire([(XX - 75, m1["GND"][1]), (XX - 75, m1["SEL"][1]), m1["SEL"]], "GND", "SEL=GND (L)")
wire([(XX - 75, m1["SEL"][1]), (XX - 75, m2["GND"][1]), m2["GND"]], "GND")
wire([lp["D1"], (XX - 30, lp["D1"][1]), (XX - 30, m1["BCLK"][1]), m1["BCLK"]], "BCLK", "BCLK")
wire([(XX - 30, m1["BCLK"][1]), (XX - 30, m2["BCLK"][1]), m2["BCLK"]], "BCLK")
wire([lp["D2"], (XX - 40, lp["D2"][1]), (XX - 40, m1["LRCL"][1]), m1["LRCL"]], "LRCL", "LRCL / WS")
wire([(XX - 40, m1["LRCL"][1]), (XX - 40, m2["LRCL"][1]), m2["LRCL"]], "LRCL")
wire([lp["D3"], (XX - 50, lp["D3"][1]), (XX - 50, m1["DOUT"][1]), m1["DOUT"]], "DOUT", "DOUT")
wire([(XX - 50, m1["DOUT"][1]), (XX - 50, m2["DOUT"][1]), m2["DOUT"]], "DOUT")

# ---- wires: microSD (SPI on D5/D8/D9/D10), 3V3 and GND buses on the right
wire([(rp["3V3"][0] + 40, y3), (rp["3V3"][0] + 100, y3), (rp["3V3"][0] + 100, sd["VCC"][1]), sd["VCC"]], "3V3")
wire([(rp["GND"][0] + 55, yg), (rp["GND"][0] + 85, yg), (rp["GND"][0] + 85, sd["GND"][1]), sd["GND"]], "GND")
wire([rp["D10"], (rp["D10"][0] + 25, rp["D10"][1]), (rp["D10"][0] + 25, sd["DI"][1]), sd["DI"]], "MOSI")
wire([rp["D8"], (rp["D8"][0] + 15, rp["D8"][1]), (rp["D8"][0] + 15, sd["SCK"][1]), sd["SCK"]], "SCK")
wire([rp["D9"], (rp["D9"][0] + 35, rp["D9"][1]), (rp["D9"][0] + 35, sd["DO"][1]), sd["DO"]], "MISO")
wire([lp["D5"], (XX - 15, lp["D5"][1]), (XX - 15, XY - 55), (rp["D7"][0] + 125, XY - 55), (rp["D7"][0] + 125, sd["CS"][1]), sd["CS"]], "CS")

# ---- wires: button
wire([rp["D7"], (rp["D7"][0] + 70, rp["D7"][1]), (rp["D7"][0] + 70, 305), (880, 305)], "BTN")
wire([(rp["GND"][0] + 85, sd["GND"][1]), (rp["GND"][0] + 85, 330), (880, 330)], "GND")
# ---- wires: LED
wire([(rp["3V3"][0] + 100, sd["VCC"][1]), (rp["3V3"][0] + 100, 400), (880, 400)], "3V3")
wire([(rp["GND"][0] + 85, 330), (rp["GND"][0] + 85, 422), (880, 422)], "GND")
wire([lp["D6"], (XX - 20, lp["D6"][1]), (XX - 20, XY + XH + 20), (rp["D7"][0] + 115, XY + XH + 20), (rp["D7"][0] + 115, 444), (880, 444)], "LED")
# ---- wires: motor
wire([(rp["3V3"][0] + 100, 400), (rp["3V3"][0] + 100, 510), (880, 510)], "3V3")
wire([(rp["GND"][0] + 85, 422), (rp["GND"][0] + 85, 535), (880, 535)], "GND")
wire([lp["D4"], (XX - 10, lp["D4"][1]), (XX - 10, XY + XH + 35), (rp["D7"][0] + 130, XY + XH + 35), (rp["D7"][0] + 130, 560), (880, 560)], "MOT")
# ---- wires: battery
wire([batp, (batp[0], 580), (520, 580), (520, 600)], "BAT+")
wire([batn, (batn[0], 570), (680, 570), (680, 600)], "BAT-")

# ---- legend / pin table
add('<text x="60" y="520" font-weight="bold">Pin map (XIAO ESP32S3, all 11 GPIO used)</text>')
rows = [("D1 / GPIO2", "I2S BCLK (both mics)"), ("D2 / GPIO3", "I2S LRCL / WS (both mics)"),
        ("D3 / GPIO4", "I2S DOUT (both mics, L/R via SEL)"), ("D7 / GPIO44", "Button, to GND, INPUT_PULLUP"),
        ("D6 / GPIO43", "NeoPixel data"), ("D4 / GPIO5", "Haptic driver (optional)"),
        ("D0 / GPIO1", "VBAT sense via 2x220 kΩ (optional)"),
        ("D5 / GPIO6", "microSD CS"), ("D8 / GPIO7", "microSD SCK"), ("D9 / GPIO8", "microSD DO (MISO)"), ("D10 / GPIO9", "microSD DI (MOSI)")]
for i, (a, b) in enumerate(rows):
    y = 542 + i * 18
    add(f'<text x="60" y="{y}" font-size="12" font-family="Menlo, monospace">{a:<18}</text>')
    add(f'<text x="200" y="{y}" font-size="12">{b}</text>')

add('</svg>')
open(OUT, "w").write("\n".join(svg))
print("wrote", OUT)
