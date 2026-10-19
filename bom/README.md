# Bill of materials — OpenPocket v0 "Basic"

Machine-readable master: [`bom.csv`](bom.csv). One row per line item, three
manufacturing categories, so each row can be routed to the right kind of supplier:

| category | how it is sourced | rows |
|---|---|---|
| `electronics` | distributors (Seeed, Adafruit, Digi-Key, Mouser, Amazon) | OP0-ELEC-* |
| `3d-print` | print yourself from the STL, or a print service | OP0-MECH-001, -002 |
| `cnc-aluminium` | any CNC shop: send the STEP + drawing PDF from `hardware/mechanical/` | OP0-MECH-003, -011, -012 (button cap, optional in the RFQ) |
| `hardware`, `consumable` | Amazon / McMaster-Carr | OP0-MECH-004 … 010 |

Columns: `required` is `yes` for the minimum working device and `optional`
for haptics and battery sensing. `file` points at the manufacturing file for
made parts. Prices are 2026-10 estimates for quantity 1 in the USA, before
shipping; they are inputs for the ordering experiment, not quotes.

## Cost at quantity 1 (estimate)

| group | USD |
|---|---|
| Electronics, required | ≈ 56 |
| Electronics, optional (haptics, VBAT) | ≈ 3 |
| Printed parts (filament) | ≈ 3 |
| Aluminium shell + lid (+ turned button cap), 1 set CNC in the USA | **unknown — the experiment** (guess 150–300) |
| Magnets, screws, tapes, glue (kits, mostly reusable) | ≈ 30 |

## Supply notes (the "design with what you can buy" angle)

- The first mic choice (InvenSense INMP441) is not recommended for new designs
  and the second (TDK ICS-43434, Adafruit 6049) was discontinued in 2026.
  Adafruit 3421 (Knowles SPH0645LM4H) is the in-stock drop-in with the same
  16.5 × 12.7 mm board. The lid uses a grille of seven Ø0.7 holes (centre +
  hexagon, pitch 0.95, ~Ø2.6 overall) over each port to tolerate a small
  port offset between the two boards.
- The tactile switch is the 5.0 mm Omron B3F-1022 (100 gf); it presses
  through the turned aluminium button cap OP0-MECH-012 (orange anodize).
  Until the cap is machined, a 3D-printed PETG cap from the same STEP works.
- The XIAO charges at only 100 mA, so the 500 mAh cell takes ~5 h. Acceptable
  for v0; a dedicated charger IC is on the list for the custom PCB version.
- The 403040 cell is a generic size sold by many brands; any cell up to
  42.5 × 31 × 4.2 mm including the protection board fits.
- Screw length: M2 × 8 flat head gives 5 mm of thread engagement in the
  blind holes of the shell bosses (drilled 6.5 deep). Do not substitute
  M2 × 10 (it would bottom out before the head seats).
