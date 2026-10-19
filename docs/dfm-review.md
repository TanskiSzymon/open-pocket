# OpenPocket v0 — manufacturability and fit review

Date: 2026-10-13, updated the same day for the slim layout (plain XIAO +
microSD breakout, 403040 cell) and again for the all-metal enclosure (shell + lid, 80 × 48 × 12.6 mm). Scope: (1) can the aluminium shell and lid actually be made,
and what will drive its price; (2) does every component have a defined place
in the enclosure or is it loose; (3) a verified buy list for the electronics
with fast delivery to San Francisco.

## 1. Machined parts: shell (OP0-MECH-003) and lid (OP0-MECH-011) — DFM

Since 13.10 (Szymon: "all exterior in metal, fancy look") the enclosure is
an aluminium shell plus an aluminium lid; the printed parts are a tray
inside the shell and the RF window insert. Drawings:
`hardware/mechanical/drawings/shell-drawing.pdf`, `lid-drawing.pdf`
(generated from the CAD parameters by `enclosure_drawings.py`; Rev B since
19.10.2026: rounded and chamfered edges, button cap, mic grilles, rounded
RF window, laser marks).

**Shell:** 6061-T6 from solid, 80 × 48 × 12.6, R5. One pocket 76.4 × 44.4 ×
7.6 (R3.2, Ø6 end mill), four Ø4.4 corner bosses left standing with blind
M2 threads (drill Ø1.6 × 6.5, thread 5), a 1.0 × 2.0 rebate around the top
of the walls for the flush lid, four Ø10.3 × 2.1 magnet pockets in the
floor (0.9 floor), USB-C opening 9.5 × 3.8 (R1.6) through the +X wall,
Ø5.0 button hole with a Ø7.0 ↓0.3 spot face through the +Y wall; C0.3 × 45°
on the USB-C opening outside. R2.0 round on the bottom outer edge, C0.3 ×
45° chamfer on the top outer edge (ideally cut after anodizing: bright,
diamond-cut edge). Laser mark "OpenPocket / open-source hardware / v0" on
the bottom face, 0.05 deep, after anodizing.

**Lid:** 6061-T6 plate 78.2 × 46.2 × 2.0, R4.1, −0/−0.1 outline so it drops
into the rebate with 0.1 per side. Four Ø2.3 through holes with 90°
countersinks Ø4.4 with R0.3 rounded mouths for M2 flat head screws; 2 acoustic grilles of 7 × Ø0.7
(centre + hexagon, pitch 0.95) over the mic ports; 11 × 33 R1.0 through RF
window with a 13 × 35 R2.0 × 1.0 underside recess for the insert flange;
laser mark "OpenPocket" on the top near the +X/−Y corner; underside recesses for the mics (0.5) and the motor (0.5). No LED
hole: the NeoPixel sits in a recess of the translucent window insert.

**Button cap (OP0-MECH-012, optional third part):** turned 6061, Ø4.6
shaft in the Ø5.0 wall hole, Ø6.2 × 0.35 flange inside the wall (captive),
domed face 0.8 mm proud of the wall, Ø3.6 bore over the B3F-1022 plunger,
orange anodize. Quoted from STEP only; a printed PETG cap works until it is
machined.

**Verdict: both are ordinary 3-axis work, nothing exotic.** The shell is a
pocket from the top plus a side operation for the two wall openings; the lid
is a thin plate machined from both sides. Every snap, rib and cradle lives
in the printed tray, so the metal stays simple. What costs money:

| feature | effect | decision |
|---|---|---|
| pocket 76.4 × 44.4 × 7.6 in a 1.8 mm wall | the main cost of the shell: ~26 cm³ removed; 7.6 deep × 1.8 walls (4:1) is routine | ±0.05 on the pocket because tray and lid must fit; R3.2 corners for a Ø6 cutter |
| rebate 1.0 × 2.0, lid flush with the top edge | the "fancy" feature: the lid disappears into the outline; same setup as the pocket | rebate +0.05/−0, lid −0/−0.1 → 0.1 clearance per side, visible seam ~0.1 mm |
| four Ø4.4 bosses with blind M2 threads | islands in a pocket are trivial; blind tapping M2 6.5 deep needs care (taps break) | drill Ø1.6 × 6.5, thread 5 min, "do not break through the floor"; M2.5 acceptable if quoted; mask for anodize |
| 0.9 mm floor under the magnet pockets | thin but fine, as before | depth ±0.05; kept |
| USB-C opening 9.5 × 3.8 R1.6 (C0.3 outside) and Ø5.0 with a Ø7.0 spot face through side walls | needs a side operation (4th axis, a flip, or EDM): the shell's second setup | unavoidable for USB; the RFQ asks how shops price it. The opening hugs the receptacle shell (+0.3 per side) and the receptacle ends 0.37 behind the outer face so a plug mates fully; Rev A/B had it 1.6 mm deep, which would not have engaged |
| lid machined from both sides | two setups, but a flat 2 mm plate: cheap | thickness 2.0 ±0.05, flatness 0.1; recesses ±0.05 because they locate the mics |
| two mic grilles, 7 × Ø0.7 each | 14 small holes through 2 mm (~3 × D): routine but cycle time and fragile drills | replaces 2 × Ø2: cleaner look, the port is shielded; the RFQ asks whether it adds cost |
| RF window 11 × 33 R1.0 through + 13 × 35 R2.0 flange recess | without a window Wi-Fi/BLE do not leave the box; the printed insert is glued from below, top seam ~0.1 | the insert is translucent and also carries the NeoPixel, so the window is the status light and the metal has no LED hole; window size is to be verified by range tests on unit 1 |
| anodize both parts in one batch | identical colour and texture; +10–25 µm changes the lid clearance by ~0.04 | quote (a) black Type II, (b) clear, (c) as machined; the 0.1 clearance already allows for the coating. Colourways: graphite (black), silver (clear), midnight blue, sage green; orange button cap on all |
| C0.3 top-edge chamfer after anodizing, laser marks | bright diamond-cut edge against the anodize; one extra operation after the coating | asked as "ideally" in the RFQ with a request to state the cost; marks 0.05 deep after anodizing |
| weight | shell ~40 g + lid ~21 g + internals ~25 g ≈ 85 g (Pocket: 52 g) | kept for v0; a 2 mm floor outside the magnet pockets would save ~10 g at the cost of a second shell setup |

Expected prices for the shell + lid set (our estimate, not a quote; the
whole point of the RFQ is to replace this table with real numbers):

| qty | as machined | + bead blast & anodize |
|---|---|---|
| 1 set | $150–300 (platform minimums dominate) | +$30–80 lot charge |
| 10 sets | $50–90 each | +$5–10 each |
| 100 sets | $25–45 each | +$2–4 each |
| 1000 sets | $15–30 each (worth asking for a different process for the shell: 4-axis, or extrusion + machining) | +$1–2 each |

Fallback if the shell quotes are silly: keep the lid in aluminium and print
the shell (the Rev B tub design is one commit back in git).

## 2. Does every part have a place? (positional check)

Method: the CAD script's parts were each translated 0.3 and 1.0 mm in ±X, ±Y,
±Z and tested for intersection with everything else. A direction with no
intersection within 1 mm means the part is free to move that way and only
tape or glue holds it (`scratchpad/loose_check.py`, results below are after
the fixes).

| part | located by | free directions | note |
|---|---|---|---|
| shell | the outside; magnets glued in its floor | none | — |
| tray | shell pocket (0.15 per side), USB-C opening, switch plunger in the button cap | none | carries every cradle; printed |
| lid | rebate (0.1 per side), 4 countersunk screws | none | flush with the shell top |
| RF insert | flange in the lid underside recess, glued | none | — |
| XIAO (plain) | 4 tray posts under the corners, −X rail (0.3), −Y rail (0.3), the microSD cradle rail on +Y (0.3), the +X wall (0.1), USB-C opening in the shell (0.3) | none within 1 mm | 1.1 mm free above the USB-C shell to the lid |
| microSD breakout | 4 posts, rails on all four sides (0.3), **snap lips** 0.5 / 0.3 mm over the PCB edges, shell wall at +Y (0.9) | none | card captive; the lips are the first FDM snap feature in the design: verify on the first print |
| battery 403040 | −X wall (0.5), end stop (0.3), 4 guide ribs (0.3), foam tape in Z, mics / LED / lid above (0.3–0.5) | none within 1 mm | cells vary ±0.5 mm: measure before fitting, ribs are 4 mm tall so a thicker cell still drops in |
| mic 1, mic 2 | 2 pegs each (Ø2.3 in Ø2.5 holes), PCB in a 0.5 mm recess on 0.2 mm tape; the battery 1 mm below | none within 1 mm | Rev A had both mics 1.0 mm below the recess floor, hanging on the pegs with an air gap over the acoustic hole: the part "floating in the air" in the viewer. Fixed |
| switch | body 0.8 mm behind the inner wall face (room for the cap flange 0.35 + travel), plunger in the cap bore, 2 tray ribs (0.8), ledge below, backstop 0.5 mm behind the base | none | Rev A had nothing behind the body. Now at X = −12 on the +Y wall beside the battery. A drop of CA on the backstop at assembly removes the 0.5 mm play |
| button cap | Ø4.6 shaft in the Ø5.0 wall hole, Ø6.2 flange inside the wall, switch plunger behind it | along its axis within the travel | inserted from the inside before the tray; the flange makes it captive |
| LED | 9.7 mm square 0.4 mm recess in the window insert (0.3 clearance) + tape; battery 0.5 below | none within 1 mm | under the RF window at the −X end; it is the part that sets the 7.6 mm cavity |
| motor | Ø10.6 × 0.4 mm recess + its own adhesive; microSD socket 0.6 below | none within 1 mm | over the microSD board |
| antenna | adhesive FPC, 8 × 22 × 1 estimate, standing across the −X end | ±Y, −Z | fine: it is a sticker. Real antenna size unknown until the XIAO arrives |
| magnets | pockets (0.15 clearance), CA glue | none | — |
| screws | blind threads in the shell bosses, countersinks in the lid | none | heads 0.3 below the face, rounded mouths |

Also changed: the LED is the Adafruit 1612 Mini Button (Flora NeoPixel is
out of stock). Since 19.10.2026 the tactile switch is the 5.0 mm B3F-1022
(100 gf) behind the aluminium button cap.

**Why 12.6 mm and not less with modules.** Height = shell floor 3.0 + pocket +
lid 2.0. The cavity must hold the tallest stack: plain XIAO 4.5 + 1.0 posts
= 5.5; microSD board 3.5 + 1.0 = 4.5; and over the battery (0.3 foam + 4.2
cell) the lid-mounted parts: mic breakout 2.3 below the recess floor (→ 7.1)
and the 3.2 mm NeoPixel (→ 7.6). There is no floor left to put the mics and
the LED beside the battery (the XIAO and the microSD board fill the USB end
between the corner bosses), so the cavity is 7.6. A 3 mm cell (303040,
~400 mAh) gives 11.2 mm by changing one parameter. Anything below ~10 mm
needs the custom PCB (v1): mics and LED soldered flat, 2.6–3 mm cell beside
the board, ~8 mm total. Rev A was 15 mm because the XIAO Sense expansion
board stacks to 8.5 mm and the 603450 cell is 6 mm.

Fit check after the changes: zero intersection between all 14 bodies, the
real Seeed and Adafruit STEP models included, all components inside the
cavity or their lid recesses.

## 3. Buy list for 2 units, shipping to San Francisco

Three orders cover everything. Prices and stock checked 2026-10-13; links are
in `bom/bom.csv` as well.

**Order A — Digi-Key** (digikey.com, ships from Minnesota; order before
8 pm CT ships same day, UPS Next Day Air reaches SF next morning, 2-day is
~$10–15). One cart:

| qty | item | Digi-Key PN | unit |
|---|---|---|---|
| 2 | Seeed XIAO ESP32S3 (plain) | 1597-113991114-ND | $7.49 (10,113 in stock) |
| 4 | Adafruit 3421 I2S mic SPH0645 | 1528-1908-ND | $6.95 (2,163 in stock) |
| 2 (+2 spare) | Omron B3F-1022 tactile 6×6×5.0, 100 gf | search "B3F-1022" (check stock) | ~$0.40 |
| 2 | 1N4148 diode (motor flyback, optional) | 1N4148FS-ND | $0.10 |
| 2 | 1 kΩ 1/4 W (motor base, optional) | CF14JT1K00CT-ND | $0.10 |
| 4 | 220 kΩ 1/4 W (VBAT divider, optional) | CF14JT220KCT-ND | $0.10 |
| 2 | 100 nF ceramic (motor, optional) | BC1084CT-ND | $0.31 |
| 2 | PN2222A NPN TO-92 (optional) | search "PN2222A" (onsemi PN2222ABU) | ~$0.20 |

**Order B — Adafruit** (adafruit.com, ships from New York, UPS 2-day or
Next Day available at checkout):

| qty | item | link | unit |
|---|---|---|---|
| 1 pack (5) | NeoPixel Mini Button PCB | https://www.adafruit.com/product/1612 | $4.95 (in stock) |
| 2 | Vibrating mini motor disc 10 × 2.7 (optional) | https://www.adafruit.com/product/1201 | $1.95 (in stock) |

The mics (3421) are also in stock at Adafruit at the same $6.95 if Digi-Key
runs out. Flora NeoPixel (1260) is out of stock there; do not wait for it.

**Order B2 — SparkFun** (sparkfun.com, ships from Colorado, UPS 2-day):

| qty | item | link | unit |
|---|---|---|---|
| 2 | microSD Transflash Breakout (push-push socket) | https://www.sparkfun.com/sparkfun-microsd-transflash-breakout.html | $5.95 (in stock) |

Digi-Key also stocks it (search BOB-00544) if one order is preferred.

**Order C — Amazon Prime** (same/next day in SF for most of these):

| qty | item | link |
|---|---|---|
| 2 | LiPo 403040 500 mAh, 4 mm, with PCM | https://www.amazon.com/dp/B0CHBGZ778 |
| alt | LiPo 403040 500 mAh, Liter | https://www.amazon.com/dp/B09FLYNRPG |
| 2 | microSD 32 GB SanDisk Ultra A1 | https://www.amazon.com/s?k=SanDisk+Ultra+32GB+microSDHC+A1 |
| 1 kit | 30 AWG silicone wire, 6 colours, TUOFENG | https://www.amazon.com/dp/B07G2SWB19 |
| 1 (20 pcs) | Ø10 × 2 mm neodymium discs (check grade; N52 preferred) | https://www.amazon.com/dp/B0C5V31YCR |
| 1 (100 pcs) | M2 × 8 flat head countersunk A2 stainless | https://www.amazon.com/s?k=M2+x+8mm+flat+head+countersunk+screws+stainless |
| 1 | 3M 9448A double-sided tape 10 mm | https://www.amazon.com/s?k=3M+9448A+double+sided+tape+10mm |
| 1 | 0.5 mm double-sided foam tape | https://www.amazon.com/s?k=0.5mm+double+sided+foam+tape |
| 1 | Kapton tape 10 mm | https://www.amazon.com/s?k=kapton+tape+10mm |
| 1 kit | heat-shrink 1.5 / 3 mm | https://www.amazon.com/s?k=heat+shrink+tubing+kit+1.5mm+3mm |
| 1 | CA glue (Loctite 401 or similar) | https://www.amazon.com/s?k=Loctite+401 |

Notes:
- 403040 cells are sold as 450–500 mAh, 4.0 × 30 × 40 mm (+2 mm PCM end).
  Measure with calipers before fitting; the enclosure allows 4.2 + 0.3 foam.
- The battery connector pitch does not matter: the lead is cut and soldered
  to the XIAO BAT pads.
- Magnets on Amazon rarely state the grade honestly; any 10 × 2 neodymium
  disc holds a phone through 0.9 mm of aluminium. K&J Magnetics D62 is the
  trustworthy alternative but is 3/8 × 1/8 in (9.5 × 3.2 mm) and would need a
  3.4 mm pocket.
- McMaster-Carr (ships from Santa Fe Springs, CA, next day to SF) has the
  M2 × 8 flat head screws too (metric 18-8 flat head Phillips);
  pick the exact row on their site, our earlier SKU guess was not verified.

Total for 2 units, required parts only: about $45 Digi-Key + $7 Adafruit +
$12 SparkFun + $65 Amazon (most Amazon items are packs that last many units) plus shipping,
plus 2 × printed parts and 2 × shell + lid sets from the RFQ.
