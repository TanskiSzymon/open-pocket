# Assembly guide — OpenPocket v0 "Basic"

Read the whole guide once before starting. Order matters: the modules go
onto the printed tray on the bench (there is no room for fingers inside the
aluminium shell), all wires are soldered to the XIAO *before* it goes onto
the tray, and the lid is tethered to the XIAO by its wires. Reference: [`../hardware/electronics/wiring.svg`](../hardware/electronics/wiring.svg)
and the renders in [`../hardware/mechanical/renders/`](../hardware/mechanical/renders/).

Enclosure outer size: 80 × 48 × 12.6 mm. Machined parts: shell (floor +
walls), lid, button cap (turned; a 3D-printed PETG cap works until the
machined one arrives). Printed parts: tray, RF window insert. Internal frame: X along
the length (USB-C end = +X), Y across (side button = +Y), Z up from the
shell floor toward the lid.

## 0. Before you start — checks that save a reprint

1. **Printed parts.** Tray printed floor down, RF insert flange down,
   lid printed top face down. Check that the four screw holes are clear
   (push a 2.3 mm drill or an M2 screw through by hand), that the two mic
   pockets in the lid are clean.
2. **Dry fit.** The tray should drop into the shell pocket with no force
   (0.15 mm per side); if it binds, sand the tray rim, never the shell. The
   lid should drop into the rebate flush with the shell top (0.1 mm per
   side). Run an M2 screw into each of the four blind tapped holes by hand.
   The button cap should slide freely in the Ø5.0 wall hole from the inside,
   flange against the inner wall face, domed face 0.8 mm proud outside.
3. **RF window.** Glue the printed insert into the lid from the underside
   (flange into the 13 × 35 R2.0 recess, plug with its rounded corners
   flush with the top); a thin ring of CA
   on the flange. Wipe the top face at once.
4. **Magnet polarity.** Hold each 10 × 2 mm magnet against the back of a
   MagSafe phone roughly where the pocket will be (±21 mm along the length,
   ±13 mm across). Mark the face that touches the phone with a marker. Glue
   each magnet into its pocket in the shell floor with the marked face DOWN
   (toward the outside face, i.e. the pocket floor). Use a drop of CA glue; wipe the excess.
   Let cure 10 minutes. Magnets end up 0.2 mm below the inner face.
5. **Components.** The XIAO is the plain ESP32S3 (no Sense expansion board).
   The microSD breakout (SparkFun BOB-00544) comes without the header
   soldered; leave it that way and wire to the pads.

## 1. Lid: mount the two microphones, LED, motor, antenna

The mics are bottom-ported: sound enters through the hole in the PCB back.
That back face must press flat against the lid, over its grille (7 × Ø0.7 holes).

1. Solder three 30 AWG signal wires to each mic breakout: **BCLK, DOUT,
   LRCL**, 80 mm long for mic 1 (far end) and 60 mm for mic 2 (USB end).
   Power is daisy-chained so the XIAO pads stay uncrowded: a 3V and a GND
   link from mic 1 to mic 2 (about 30 mm), then one 3V and one GND wire
   (60 mm) from mic 2 to the XIAO. Leave SEL for now.
2. On **mic 1** bridge SEL to GND with a short wire (LEFT channel). On
   **mic 2** bridge SEL to 3V (RIGHT channel). Write "L" and "R" on the
   boards with a marker.
3. Put a ring of 0.2 mm double-sided tape on the PCB back around the port
   hole (leave the hole open; this is the acoustic seal). Drop the board into
   its lid recess, holes over the two pegs, wire row toward the +Y side.
   Press down. Shine a light through the lid grille: you should see the port.
4. **LED (NeoPixel Mini Button, Adafruit 1612):** tape it into the 9.7 mm
   square 0.4 mm recess on the underside of the RF window insert, LED facing
   the insert (the translucent insert is the diffuser), centred at
   (−31.5, 11.2). Wires: 3V3 (+), GND (−), DIN (DI). 60 mm.
5. **Motor (optional):** stick the coin motor into its Ø10.6 recess under
   the lid at (28, 15.5), the +X/+Y corner, so it sits over the microSD
   breakout once the lid is closed; leads toward the XIAO. Build the driver
   inline on the motor leads and heat-shrink it:
   - motor + and the 1N4148 cathode → a wire to **BAT+** (not 3V3);
   - motor − and the 1N4148 anode → PN2222A collector;
   - 100 nF across the motor terminals, 10 µF from motor + to the emitter
     (GND) side, both at the motor;
   - base → 470 Ω → CTRL wire (to D7); 10 kΩ from base to emitter (keeps the
     motor off while the XIAO boots);
   - emitter → its own GND wire to the XIAO GND pad (not shared with the
     mics).
6. **Antenna:** plug the U.FL connector onto the XIAO now (press one edge,
   then the other; it clicks). Stick the FPC antenna to the underside of the
   RF window insert, centred at (−31.5, −5.5), long side along Y, on the −Y
   side of the LED. The window spans X −37 … −26 and Y −16.5 … 16.5: no part of the
   antenna may sit under solid aluminium, and it must not touch mic 1
   (X −23.8 … −7.3). The cable runs down to the XIAO.

## 2. XIAO: solder everything to it on the bench

All signal wires go to the castellated pads on the **underside** of the XIAO
(keeps the top flat under the lid). Tin each pad, then lay the pre-tinned wire
along the castellation and reflow. Keep solder blobs under 0.7 mm tall; the
board sits on 1.0 mm corner posts.

**microSD breakout:** six wires on the pad side (the side without the
socket), 40 mm: VCC → 3V3, GND, CS → D5, DI → D10, SCK → D8, DO → D9.
Keep the solder flat; the board also sits on 1.0 mm posts. The breakout has
no resistors or capacitors of its own, so add them at its pads first:
10 kΩ from VCC to each of CS, DO, DAT1 (socket pin 8) and DAT2 (socket
pin 1; neither has a header pad, solder to the socket lead), and 10 µF +
100 nF from VCC to GND. Lay them flat on the socket side beside the socket,
never on the pad side (1.0 mm posts) and not under the motor. The CAD does
not model these parts; check the fit on unit 1.

**Passives at the XIAO:** the 33 Ω goes in series in the BCLK wire and the
100 kΩ from the DOUT wire to GND, both within ~15 mm of the XIAO pads,
heat-shrunk and laid beside the XIAO (never under it: 1.0 mm posts).

**VBAT divider (optional):** 220 kΩ from BAT+ to the D0 wire, 220 kΩ from
D0 to GND, 100 nF from D0 to GND, built inline next to the XIAO and
heat-shrunk.

| XIAO pad | to | wire |
|---|---|---|
| 3V3 | mic chain 3V (from mic 2), LED +, microSD VCC | red |
| GND | mic chain GND (from mic 2), microSD GND, motor emitter (own wire, optional), one splice wire for LED −, switch contact B, 100 kΩ, (divider) | black |
| BAT+ | battery red lead, (motor + and divider top: splice to the red lead first) | red |
| D1 / GPIO2 | 33 Ω in series → mic 1 BCLK, mic 2 BCLK | blue |
| D2 / GPIO3 | mic 1 LRCL, mic 2 LRCL | green |
| D3 / GPIO4 | mic 1 DOUT, mic 2 DOUT; 100 kΩ to GND | purple |
| D4 / GPIO5 | switch contact A | orange |
| D6 / GPIO43 | LED DIN | white |
| D7 / GPIO44 | motor driver CTRL via 470 Ω (optional) | brown |
| D0 / GPIO1 | VBAT divider midpoint + 100 nF to GND (optional) | yellow |

The mic SEL pins are bridged on the mic boards (step 1.2), not wired to the
XIAO. Where two wires share a pad, twist and tin them together first; no pad
should take more than four 30 AWG wires, so join the small GND returns on
one splice wire.

**Switch (Omron B3F-1022, 6 × 6, 5.0 mm, 100 gf):** clip the four legs to 1 mm and bend
them flat against the body *sides* (not the base: the base sits 0.5 mm from
the cradle backstop). Solder a 60 mm wire to two legs on opposite sides of
the body (they are one contact pair; check with a meter: open at rest,
closed when pressed). Contact A goes to D4, contact B to GND. Keep solder low; the cradle ribs leave 0.8 mm per side.

**Battery, last and carefully.** The XIAO battery pads are on the underside:
**BAT− is the pad nearest the USB-C connector, BAT+ is the one away from
it.** Wrong polarity destroys the charger. Procedure: tape the black lead to
the bench, solder red to BAT+, then untape black and solder it to BAT−.
Never let the bare leads touch. Cover both pads with Kapton. If the motor
or the VBAT divider is fitted, splice their BAT+ wires to the red lead
(heat-shrink) before the red lead goes onto BAT+.

Now power the board from USB-C: the XIAO's charge LED should light and, if
you flash the test firmware (`firmware/` — not part of this v0 release),
the mics, LED and button can be checked before closing the box. Check that
the motor stays still through power-up and reset.

## 3. Onto the tray, then into the shell

1. Tray on the bench, USB-C end at +X, the button cradle at +Y.
2. Drop the switch into its cradle (X = −12 on the +Y side): body between
   the two ribs, plunger pointing outward (the body front ends 0.8 mm short
   of the inner wall face once the tray is in the shell). Put a drop of
   CA between the body base and the backstop rib so the body cannot creep
   back when the button is pressed. Cover the legs with Kapton.
3. Lower the XIAO into its cradle at the +X end, −Y side: PCB on the four
   corner posts, inside the rails, USB-C overhanging the tray edge by
   1.5 mm (it will sit inside the wall opening).
4. microSD breakout into its cradle beside the XIAO (+Y side), socket up,
   card edge toward the +Y wall: slide the PCB edge under the 0.5 mm lip on
   the −X rail, then press the +X edge down past the 0.3 mm snap lip. Push a
   microSD card in until it clicks. It stays inside for good; the walls
   have no slot.
5. **Button cap first.** From inside the empty shell, push the button cap
   (OP0-MECH-012, domed face first) into the Ø5.0 hole in the +Y wall until
   its Ø6.2 flange sits against the inner wall face; the flange keeps it
   captive. Hold it there with a strip of masking tape on the outside until
   the tray is in.
6. Lower the loaded tray into the shell pocket, USB end first and slightly
   tilted so the USB-C receptacle enters its wall opening, then the switch
   plunger into the cap bore (Ø3.6). Remove the tape and press the cap from
   outside: it should click. Plug a USB-C cable: it must seat with a click and the overmold
   should touch the wall. The tray floor sits on the aluminium; the battery area is
   a cutout.
7. Stick a 0.3 mm foam pad on the aluminium floor in the battery cutout
   (−37 … +5 along X). Lay the battery between the end stop and the −X
   wall, inside the four guide ribs, leads toward the XIAO. Route the leads along the −Y wall to
   the pads. The battery top is 3.1 mm below the lid; the mics, LED and
   antenna hang 0.3–0.5 mm above it.
8. Dress the wires: mic, LED and antenna wires run along the −Y wall above
   the battery; switch wires stay at the +Y wall; microSD wires drop
   straight to the XIAO. No wire may cross the XIAO or the microSD socket
   (1.1 mm and 3.1 mm under the lid respectively).

## 4. Close

1. Lower the lid into the rebate: the mics, LED and antenna face down over
   the battery, the motor over the microSD board. Make sure no wire is
   pinched between the lid and the rebate ledge; the lid must sit flush all
   round before any screw goes in.
2. Drop the four M2 × 8 flat head screws into the countersinks and drive
   them into the blind threads in the shell bosses. Tighten until the heads
   are flush; then an eighth turn more. Do not strip the aluminium threads.
3. Press the side button: it should click. Plug USB-C: it should seat fully.
   Put the device on a MagSafe phone: it should snap on in one orientation.

## Order summary

```
shell magnets glued, RF insert glued into the lid  →  lid: mics / LED / motor / antenna taped + wired
→  XIAO: all wires soldered (signals, switch, battery last)  →  bench test on USB
→  tray on the bench: switch, XIAO, microSD board snapped in, card in
→  button cap into the shell wall from inside  →  tray into the shell
→  foam + battery  →  dress wires  →  lid into the rebate  →  4 screws  →  function check
```

## Why this order

- The shell pocket is 7.6 mm deep and 1.8 mm walls leave no room for
  fingers or tweezers, so everything that needs pressing (switch, snap lips)
  is done on the tray outside, and the loaded tray drops in once.
- Soldering the XIAO underside pads is only possible with the board out of
  the cradle; therefore every wire, including the battery, is attached first
  and the lid is tethered before the XIAO is seated.
- The battery is soldered last on the bench because a live LiPo is the only
  energised thing in the build; everything else is dead until then.
- Magnets are glued first so the glue cures while you solder, and so the
  polarity check happens before the floor is covered by the tray.
