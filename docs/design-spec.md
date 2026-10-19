# OpenPocket v0 "Basic" — design spec

Date: 2026-10-13, enclosure updated 2026-10-19. Status: mechanical and
electrical design done; build not started.

## Purpose

1. A working open-source recorder in the spirit of Pocket (heypocket.com):
   two mics, battery, USB-C charging, Wi-Fi/BLE, records to microSD, sends
   recordings or transcripts to a laptop or phone.
2. Buildable by one person: distributor electronics, two 3D-printed parts
   and two CNC aluminium parts, all in one bill of materials.

## Scope of v0

In: enclosure, wiring, BOM, assembly guide, machining drawings, firmware
specification (`firmware-spec.md`). Modules only, no custom PCB. No screen,
no fingerprint reader, no on-device transcription. The laptop does the
transcription: the receiver is **pocket-libre**, an existing open-source
client for the original Pocket, which our firmware targets protocol-for-
protocol (`related-work.md`).

Out (later versions): firmware and receiver, screen with a face, fingerprint
approval of agent actions, Linux SoC variant with local transcription,
custom PCB, pendant and clip variants.

## Decisions and why

| decision | choice | reason |
|---|---|---|
| MCU | XIAO ESP32S3 (plain) + SparkFun microSD breakout (BOB-00544) | the Sense expansion board stacks to 8.5 mm and set the old 15 mm height; the plain board is 4.5 mm, $7.49, STEP available; microSD moves to a 3.5 mm breakout beside it |
| Local transcription | no | ESP32 cannot run it; a Linux SoC costs 10× the power budget. Planned as "Pro" variant |
| Mics | 2 × Adafruit 3421 (SPH0645) | I2S, bottom port, in stock; INMP441 is NRND and ICS-43434 discontinued |
| Battery | LiPo 403040 500 mAh, 4 mm | ~10 h recording at 32 kbps MP3, ~3 days standby; 4 mm cell + mic breakout above it sets the 7.6 mm cavity |
| Form | flat slab with MagSafe magnets | closest to the original; gives a natural aluminium part |
| Enclosure | **all-metal exterior**: aluminium shell (floor + walls, one pocket, lid rebate) + aluminium lid flush in the rebate; everything inside on a printed tray | Szymon's call (13.10): looks better, cleaner build; two CNC parts (one simple, one two-sided) are a richer RFQ test than a flat plate |
| RF window | 11 × 33 mm through cutout in the lid with a translucent printed insert flush on top; the FPC antenna and the NeoPixel sit under it | Wi-Fi/BLE do not pass through aluminium; the one window also becomes the status light, so the metal has no LED hole |
| USB-C | XIAO placed so the receptacle ends 0.37 mm behind the outer face; wall opening 9.5 × 3.8 with R1.6 ends around the receptacle shell | a plug must mate 6.5 mm; a receptacle recessed 1.6 mm behind the wall (Rev A/B) would not have engaged fully |
| microSD | captive: breakout inside, no wall slot, card inserted at assembly | cleaner walls (only USB-C and the button); recordings leave by USB MSC / BLE / Wi-Fi anyway |
| Fastening | 4 × M2 × 8 countersunk flat head from the lid into blind M2 threads in the shell bosses | flush screws, 5 mm engagement, no inserts, threads are a quoting feature |
| Printed parts | tray (floor plate with all cradles, battery cutout) + RF window insert | all snap features and fine ribs stay in plastic; the metal parts stay simple |
| Button | side-mounted 6 × 6 × 5.0 tactile (Omron B3F-1022, 100 gf) in a printed cradle with backstop, body 0.8 mm behind the inner wall face, pressing through a turned aluminium cap (OP0-MECH-012, orange anodize) held captive by its flange inside the wall | like the original's side button; keeps the lid flat; a metal button in an accent colour instead of a bare plastic plunger |
| Finish and colourways | graphite (black anodize), silver (clear anodize), midnight blue, sage green; orange button cap on all. Shell bottom edge R2.0, top edge C0.3 chamfer cut after anodizing (bright edge); laser marks after anodizing | product look; a colour is only a different anodize, the geometry stays the same |
| Protocol | Pocket-compatible BLE / Wi-Fi AP / USB MSC protocol as reverse-engineered in pocket-libre `PROTOCOL.md` | the desktop client (sync, Whisper, diarization, summaries) already exists, is MIT and maintained; we do not write a receiver |
| Audio format | MP3 16 kHz mono 32 kbps, files `RECORD/YYYYMMDD/YYYYMMDDHHmmss.mp3` | identical to the original so pocket-libre's size accounting and Whisper pipeline work unchanged; 14 MB per hour |
| Two mics, mono output | keep 2 × SPH0645 at 27 mm, mix to mono in firmware | the original is mono too; two mics are for noise reduction, not stereo |
| Security | plain protocol by default (as the original), BLE Secure Connections + encrypted link as an opt-in extension | compatibility first; the original has no encryption at all, we can do better without breaking clients |
| Status LED | Adafruit 1612 NeoPixel Mini Button in a lid recess | Flora NeoPixel out of stock; smaller, locating recess instead of tape-only |

## Enclosure numbers

- Outer 80.0 × 48.0 × 12.6 mm (shell floor 3.0 + pocket 7.6 + lid 2.0),
  R5 corners. Was 80 × 46 × 15 with the XIAO Sense, a 6 mm cell and a
  printed tub (Rev A); 80 × 48 × 12.2 printed-tub slim (Rev B).
- Shell: 6061-T6 from solid, pocket 76.4 × 44.4 × 7.6 (R3.2), 1.8 mm walls,
  rebate 78.4 × 46.4 × 2.0 at the top, four Ø4.4 corner bosses with blind
  M2 threads, four Ø10.3 × 2.1 magnet pockets in the floor, USB-C opening
  9.5 × 3.8 (R1.6, C0.3 × 45° on the outer face) in the +X wall, Ø5.0
  button hole with a Ø7.0 ↓0.3 spot face outside in the +Y wall. Outer
  edges: R2.0 round at the bottom, C0.3 × 45° chamfer at the top (ideally
  cut after anodizing for a bright edge). Laser mark "OpenPocket /
  open-source hardware / v0" on the bottom face, 0.05 deep, after
  anodizing. Drawings: Rev B (19.10.2026).
- Lid: 78.2 × 46.2 × 2.0 plate flush in the rebate (0.1 per side), four
  countersunk M2, two acoustic grilles of 7 × Ø0.7 holes (centre +
  hexagon, pitch 0.95) over the mic ports, 11 × 33 RF window with R1.0
  corners and a 13 × 35 R2.0 underside flange recess (1 mm), small laser
  mark "OpenPocket" on the top near the +X/−Y corner, underside recesses for the mics (0.5) and the
  motor (0.5). The translucent window insert carries the antenna and has a
  0.4 mm recess for the NeoPixel: the window is the status light.
- Button: Omron B3F-1022 (6 × 6, 5.0 mm, 100 gf), body 0.8 mm behind the
  inner wall face (room for the cap flange 0.35 + travel). Cap
  OP0-MECH-012: turned 6061, Ø4.6 shaft in the Ø5.0 hole, Ø6.2 × 0.35
  flange inside the wall (captive), domed face 0.8 mm proud of the wall,
  Ø3.6 bore over the plunger, orange anodize; a printed PETG cap works
  until the machined one exists.
- Tray: printed 0.6 mm floor plate with a 2 mm rim, XIAO and microSD
  cradles (posts, rails, snap lips), battery cutout with ribs and an end
  stop, switch cradle. Drops into the pocket with 0.15 mm per side.
- XIAO (plain) on the tray at the USB end, PCB edge 0.1 mm from the wall so
  the USB-C receptacle sits inside the wall opening, 0.37 mm behind the
  outer face; microSD breakout beside it, card captive (no slot).
- Battery 403040 at the −X end on the aluminium floor (0.3 mm foam)
  through the tray cutout; mics, LED and antenna hang from the lid above
  it (0.3–0.5 mm clearance), the motor above the microSD board.
- Mics taped under the lid in 0.5 mm recesses (0.2 mm tape) with two
  locating pegs each, the PCB back pressed flat against the lid over a
  7 × Ø0.7 grille; positions (−28, 0) and
  mic 1 (−17.5, 8.5) and mic 2 (3.5, −8.5) → 27 mm baseline. LED and
  motor sit in 0.4 mm recesses.
- Every part is located by geometry (walls, rails, posts, pegs, recesses);
  tape and glue only hold, never locate. See `docs/dfm-review.md` for the
  positional check of every part.
- Magnets at (±21, ±13), i.e. on a Ø49 circle, inside the MagSafe ring.
- Fit check: zero intersection between all parts, all components inside
  the cavity (mics, LED and motor inside their lid recesses), verified
  against the real Seeed STEP model (camera removed).

## Roadmap: v0 → v0.5 Slim → v1 custom PCB

The teardown shows the original gets its thickness from a 2.6 mm pouch cell
(265448, 840 mAh) and a bare ~55 × 30 mm PCB. Height budgets:

| variant | electronics | battery | height budget | total | cost delta |
|---|---|---|---|---|---|
| v0 Rev A (superseded) | XIAO Sense stack 8.5 + 1.2 posts, mic breakouts under the lid | 603450, 6.2 mm, 1000–1200 mAh | plate 3 + cavity 10.4 + lid 1.6 | 15 mm | — |
| v0 Rev B printed tub (superseded) | plain XIAO (4.5 mm) + microSD breakout (3.5 mm) side by side, mics/LED under the lid over the 4 mm cell | 403040, 4.2 mm, 500 mAh | plate 3 + cavity 7.6 + lid 1.6 | 12.2 mm | — |
| **v0 Basic, metal** (this design) | same internals on a printed tray inside an aluminium shell, aluminium lid with RF window | 403040, 4.2 mm, 500 mAh | shell floor 3 + pocket 7.6 + lid 2.0 | **12.6 mm** | shell + lid CNC ~$150–300 at qty 1 instead of a $60–130 plate |
| v0 with a 3 mm cell | same | 303040, ~400 mAh | plate 3 + cavity 6.6 + lid 1.6 | ~11.2 mm | one parameter |
| v1 custom PCB | ESP32-S3-WROOM-1 / MINI-1, SPH0645 soldered with port holes, microSD, USB-C mid-mount, MCP73831, ~4 mm stack beside the cell | 2.6–3 mm cell, ~800 mAh | plate 2 + cavity ~4.5 + lid 1.2 | **~8 mm** | NRE ~25–40 h design, prototypes ~$150–200 for 2 iterations, ~$30–43 per assembled board at qty 2, ~$15–18 at 100 |

The firmware specification applies to all three; only the pin map changes.

## Open questions

1. Button: B3F-1022 (5.0 mm, 100 gf) behind the aluminium cap; check the
   travel and click through the cap on unit 1 (printed PETG cap first).
2. Antenna placement under the lid near the battery and 10 mm from the
   aluminium: expect reduced Wi-Fi range; measure on the first build.
3. XIAO charging at 100 mA → ~5 h for 500 mAh. Fine.
4. SPH0645 vs ICS-43434 port position: the 7-hole Ø0.7 grille should
   cover it; verify on the first lid with a light.
5. Battery sense divider (D0) and haptics are optional; firmware decides.
6. pocket-libre scans for the `PKT01_` name pattern; check whether it
   accepts another name or send a small PR so OpenPocket can advertise as
   `OPENPOCKET_…`.
7. Lid light hole and the NeoPixel: the original has an RGBW LED; ours is
   RGB. Fine for status, not a copy.
8. microSD is captive: insert the card before the lid goes on. Normal use
   never removes it (USB MSC, BLE, Wi-Fi).
9. Snap lips over the microSD PCB (0.5 and 0.3 mm) are the first FDM
   snap feature in the design: check they survive printing and insertion.
10. RF window: 11 × 33 mm (antenna ~8 × 22 plus the LED) is a guess at what
    the FPC antenna needs; measure Wi-Fi range on unit 1 and widen the
    window in the lid parameter if needed. The insert must be translucent
    (smoke PETG or acrylic) so the LED shows; black anodize hides the seam.
11. Weight: shell ~40 g + lid ~21 g + internals ~25 g ≈ 85 g (the original
    is 52 g). A 2 mm floor outside the magnet pockets would save ~10 g; not
    done for v0 to keep the shell a single-setup part.

## Next steps

1. Order parts for 2 units (electronics ≈ $130) and print tray + RF insert;
   print the shell and lid once in PLA as a fit check before the RFQ parts arrive.
2. Get the shell and lid quoted by a few CNC shops (STEP + drawing PDF).
3. Build unit 1, record the fit problems, adjust parameters, re-export.
4. Firmware per `firmware-spec.md`: MP3 mono to microSD, Pocket-compatible
   BLE / Wi-Fi AP / USB MSC protocol, test against pocket-libre.
5. MakerWorld listing: tray + RF insert + printable shell/lid for a plastic
   build + assembly guide + BOM link.
