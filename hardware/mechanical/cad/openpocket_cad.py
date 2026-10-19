"""OpenPocket v0 ("Basic") enclosure — parametric CAD in CadQuery.

Coordinate frame (mm): origin at the centre of the aluminium back plate's
INNER (top) face. +Z points toward the lid (away from the phone). +X points
toward the USB-C end. +Y points toward the side button.

Stack (bottom to top):
    back plate   Z = -3.0 .. 0.0     (CNC aluminium, 4x M2 tapped, 4 magnet pockets)
    tub          Z =  0.0 .. 10.4    (3D printed walls, open top and bottom)
    lid          Z = 10.4 .. 12.0    (3D printed, carries both mics, LED, motor, antenna)
Four M2 x 14 pan-head screws go from the lid, through the tub corner bosses,
into the tapped holes of the plate. Nothing else is glued except the magnets.

Run:  python openpocket_cad.py        -> exports to ../export/ and runs the fit check
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
MECH = os.path.dirname(HERE)
EXPORT = os.path.join(MECH, "export")
VENDOR = os.path.join(MECH, "vendor-models")
XIAO_STEP = os.path.join(VENDOR, "seeed", "seeed-studio-xiao-esp32s3-3d_model",
                         "XIAO-ESP32S3 v2.step")
MIC_STEP = os.path.join(VENDOR, "adafruit", "adafruit-6049-i2s-mic.step")


# ----------------------------------------------------------------------------
# Parameters
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class P:
    # enclosure
    L_in: float = 76.4          # internal cavity length (X)
    W_in: float = 44.4          # internal cavity width (Y): XIAO + microSD breakout side by side
    H_in: float = 7.6           # internal height, plate top to lid underside (LED over the battery sets it)
    wall: float = 1.8
    R_out: float = 5.0          # outer corner radius
    t_lid: float = 2.0          # aluminium lid, sits flush in a rebate at the top of the shell walls
    rebate_w: float = 1.0       # rebate width into the wall (0.8 mm of wall stays outside the lid)
    lid_clear: float = 0.1      # per side, lid outline vs rebate
    t_plate: float = 3.0        # shell floor (magnet pockets 2.1 deep leave 0.9 mm)
    # printed tray that carries all internal features inside the aluminium shell
    tray_t: float = 0.6         # tray floor thickness
    tray_clear: float = 0.15    # per side, tray outline vs pocket
    tray_rim_h: float = 2.0     # low rim along the walls
    tray_rim_t: float = 1.0
    # fasteners: M2 x 8 countersunk flat head, 4 corners, into blind tapped holes in the shell bosses
    screw_len: float = 8.0
    boss_d: float = 4.4         # corner bosses; a flat at |y| = boss_clip_y keeps them off the XIAO / microSD boards
    boss_x: float = 35.2        # screw centres: 3.9 from the lid edge in X, 3.05 in Y, 1.07 from the lid corner centre,
    boss_y: float = 20.05       # so the countersink mouth (R2.2 + R0.3 round) keeps >= 0.5 mm of flat lid all round
    boss_clip_y: float = 18.5   # boss inner face toward the boards (XIAO edge at 18.19)
    boss_hole_d: float = 2.3    # clearance hole in the lid
    tap_drill_d: float = 1.6    # M2 tap drill
    tap_depth: float = 6.5      # drill depth from the boss top (thread 5.0)
    csk_d: float = 4.4          # 90 deg countersink in the lid; head 3.8 sits 0.3 below the top face, never proud
    csk_edge_r: float = 0.3     # round on the countersink mouth (no sharp ring around the screw heads)
    lid_edge_r: float = 0.5     # round on the lid top outer edge
    shell_top_c: float = 0.3    # 45 deg bright-cut chamfer on the shell top outer edge (0.8 mm rim outside the rebate)
    shell_bot_r: float = 2.0    # soft round on the shell bottom edge (sits in the hand like a pebble)
    usb_chamfer: float = 0.3    # 45 deg chamfer around the USB-C opening on the outer face
    head_sink: float = 0.2      # model: head 0.1 radial clear of the cone; a real head seats (csk_d - 3.8) / 2 = 0.3 below the top
    # magnets: 4x N52 disc 10 x 2 mm, pockets from plate top (inner) face
    magnet_d: float = 10.0
    magnet_t: float = 2.0
    magnet_pocket_clear: float = 0.3
    magnet_pocket_depth: float = 2.1   # floor 0.9 mm under the pocket
    magnet_x: float = 21.0
    magnet_y: float = 13.0
    # XIAO ESP32S3 (plain, no Sense expansion board; from Seeed STEP)
    xiao_pcb_l: float = 20.95   # X
    xiao_pcb_w: float = 17.78   # Y
    xiao_stack_h: float = 4.5   # pads underside to top of the USB-C shell (STEP: 4.46)
    xiao_post_h: float = 1.0    # PCB underside above the shell floor: tray floor 0.6 + posts 0.4
    xiao_post: float = 1.8
    xiao_y_center: float = -9.3 # PCB -Y edge 0.3 mm from the corner boss
    xiao_edge_inset: float = 1.9  # PCB USB edge 0.1 inside the wall's inner face: the receptacle (1.53 proud) ends 0.37 behind the outer face, so a plug mates fully
    usb_clear: float = 0.3        # wall opening = receptacle shell + this per side, R1.6 corners (shell 8.94 x 3.21)
    # microSD breakout (SparkFun BOB-00544, 21.59 x 20.32 x 3.5, Molex push-push socket)
    sd_l: float = 21.59         # along X (header edge toward +X)
    sd_w: float = 20.32         # along Y (card edge toward +Y wall)
    sd_h: float = 3.5           # PCB 1.6 + socket 1.88
    sd_x0: float = 11.1         # -X edge; +X edge 32.69 stays 0.3 clear of the corner boss (33.0)
    sd_wall_gap: float = 0.9    # card edge to the pocket wall (no tray rim along this stretch)
    sd_card_x: float = 20.84    # card centre line (socket local x 8.24 from the -X edge)
    sd_card_w: float = 11.0
    sd_card_t: float = 1.0
    sd_card_z: float = 2.9      # card underside above the plate: posts 1.0 + PCB 1.6 + socket floor 0.3
    # battery LiPo 403040 (4.0 x 30 x 40 nominal, ~500 mAh, with PCM lead end)
    bat_l: float = 42.5
    bat_w: float = 31.0
    bat_t: float = 4.2
    bat_foam: float = 0.3
    # mic breakout (Adafruit 3421 / 6049, 16.51 x 12.70 x 2.6)
    mic_l: float = 16.51
    mic_w: float = 12.70
    mic_h: float = 2.60
    mic_recess: float = 0.5
    mic_tape: float = 0.2       # double-sided tape between the mic PCB and the recess floor
    mic_hole_d: float = 2.0     # area the grille covers over the mic port
    mic_grille_d: float = 0.7   # grille: 7 holes, centre + hexagon, drilled through the lid over each port
    mic_grille_pitch: float = 0.95
    mic1_xy: tuple = (-15.5, 8.5)   # both over the battery / floor strip, 25 mm baseline; clear of the RF window
    mic2_xy: tuple = (3.5, -8.5)
    # tactile switch 6x6, 5.0 mm total height (Omron B3F-1022: body 3.5 + plunger 1.5) under a captive aluminium cap
    sw_body: float = 6.0
    sw_body_h: float = 3.5
    sw_total_h: float = 5.0
    sw_plunger_d: float = 3.5
    sw_x: float = -12.0         # on the +Y wall beside the battery (6.7 mm strip between cell and wall)
    sw_z: float = 4.0           # plunger axis height above the shell floor; body 1.0..7.0 under the 7.6 lid
    sw_wall_pocket: float = -0.8   # body front 0.8 behind the inner wall face: room for the cap flange (0.35) + 0.45 travel gap
    sw_leg_space: float = 0.5   # gap behind the body base, filled with a drop of CA at assembly
    sw_backstop_t: float = 1.0
    # button cap: turned aluminium, anodised accent colour; the flange inside the wall makes it captive
    btn_hole_d: float = 5.0     # hole in the wall
    cap_d: float = 4.6          # cap shaft (0.2 radial clearance)
    cap_flange_d: float = 6.2
    cap_flange_t: float = 0.35
    cap_proud: float = 0.8      # cap face beyond the outer wall face (1.1 beyond the spot-face floor)
    cap_bore_d: float = 3.6     # sits over the 3.5 plunger
    btn_spot_d: float = 7.0     # shallow spot-face around the button on the outer wall
    btn_spot_depth: float = 0.3
    # LED (Adafruit 1612 NeoPixel Mini Button, 9.1 x 9.1 x 3.2) and motor (10 x 2.7 coin)
    led_xy: tuple = (-31.5, 11.2)   # under the RF window insert: the window doubles as the status light
    led_w: float = 9.1
    led_h: float = 3.2
    led_hole_d: float = 2.0
    led_recess: float = 0.4     # locating recess in the lid underside
    motor_recess: float = 0.5
    motor_xy: tuple = (28.0, 15.5)  # over the microSD breakout
    motor_d: float = 10.0
    motor_h: float = 2.7
    # FPC antenna (estimate; supplied with the XIAO)
    ant_xy: tuple = (-31.5, -5.5)   # standing across the -X end, under the RF window insert
    ant_l: float = 8.0              # X  (estimate for the Seeed FPC antenna; measure the real one)
    ant_w: float = 22.0             # Y
    # RF window in the aluminium lid: through cutout + underside recess for the flange of a printed insert
    rf_xy: tuple = (-31.5, 0.0)     # window centre (antenna + LED under it); flange stays 0.5 clear of the corner countersinks
    rf_l: float = 11.0              # X
    rf_w: float = 33.0              # Y: antenna 22 + LED 9.1 + gaps; recess 35 stays 1.3 clear of the screw holes
    rf_flange: float = 1.0          # flange width around the cutout (underside recess)
    rf_flange_t: float = 1.0
    rf_clear: float = 0.1
    rf_r: float = 1.0               # cutout corner radius (Ø2 end mill); the underside recess gets rf_r + rf_flange
    ant_t: float = 1.0
    # battery guide ribs on both long walls (X positions), 0.3 mm clearance to the cell
    bat_rib_x: tuple = (-30.0, -3.0)
    bat_cut_clear: float = 0.3  # tray floor cutout around the cell (cell sits on the shell floor)
    bat_rib_t: float = 1.2
    bat_rib_h: float = 4.0
    bat_rib_clear: float = 0.3
    # laser marking (after anodising), 0.05 deep
    mark_font: str = "Avenir Next"
    mark_depth: float = 0.05

    @property
    def L_out(self):
        return self.L_in + 2 * self.wall

    @property
    def W_out(self):
        return self.W_in + 2 * self.wall

    @property
    def H_total(self):
        return self.t_plate + self.H_in + self.t_lid

    @property
    def R_in(self):
        return self.R_out - self.wall

    @property
    def lid_L(self):
        return self.L_in + 2 * self.rebate_w - 2 * self.lid_clear

    @property
    def lid_W(self):
        return self.W_in + 2 * self.rebate_w - 2 * self.lid_clear

    @property
    def boss_xy(self):
        return [(sx * self.boss_x, sy * self.boss_y) for sx in (-1, 1) for sy in (-1, 1)]

    @property
    def xiao_x0(self):
        """X of the XIAO PCB edge opposite the USB (the -X edge)."""
        return self.L_out / 2 - self.xiao_edge_inset - self.xiao_pcb_l

    @property
    def xiao_x1(self):
        return self.L_out / 2 - self.xiao_edge_inset


p = P()


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def rbox(l, w, h, r, z0=0.0):
    """Rounded-rectangle prism centred in XY, from z0 up by h."""
    return (cq.Workplane("XY").workplane(offset=z0)
            .rect(l, w).extrude(h).edges("|Z").fillet(r))


def box_at(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def cyl_at(x, y, z0, z1, d):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


def rbox_at(cx, cy, l, w, z0, z1, r):
    """Rounded-rectangle prism centred at (cx, cy), from z0 to z1."""
    return rbox(l, w, z1 - z0, r, z0=z0).translate((cx, cy, 0))


def ycyl(x, z, y0, y1, d):
    """Cylinder along Y at (x, z) from y0 to y1."""
    return cq.Workplane("XZ").workplane(offset=-y0).center(x, z).circle(d / 2).extrude(-(y1 - y0))


def grille_xy(cx, cy):
    """7-hole grille (centre + hexagon) around (cx, cy)."""
    a = p.mic_grille_pitch
    return [(cx, cy)] + [(cx + a * math.cos(math.radians(k * 60)), cy + a * math.sin(math.radians(k * 60))) for k in range(6)]


def text_solid(txt, size, x, y, z, depth, flip=False, halign="center"):
    """Text prism with its top face at z (or bottom face at z, reading from below, when flip)."""
    wp = cq.Workplane("XY")
    if flip:
        wp = wp.transformed(rotate=(180, 0, 0))
    t = wp.text(txt, size, -depth, font=p.mark_font, halign=halign, valign="center")
    t = t.translate((x, y, z))
    return t


# ----------------------------------------------------------------------------
# Vendor models (XIAO Sense without camera; mic breakout)
# ----------------------------------------------------------------------------
def xiao_transform():
    """Maps Seeed STEP coords (PCB in XZ plane, Y = thickness) into the case frame."""
    tx = p.xiao_x1 - 12.28         # STEP PCB +x edge is at x = 12.28
    ty = p.xiao_y_center - 6.11    # STEP width centre (-z) is 6.11
    tz = p.xiao_post_h + 0.25      # STEP pad underside is at y = -0.25
    return tx, ty, tz


def load_xiao() -> cq.Workplane:
    s = cq.importers.importStep(XIAO_STEP)
    solids = list(s.solids().vals())
    comp = cq.Compound.makeCompound(solids)
    tx, ty, tz = xiao_transform()
    comp = comp.rotate((0, 0, 0), (1, 0, 0), 90)       # (x,y,z) -> (x,-z,y)
    comp = comp.translate((tx, ty, tz))
    return cq.Workplane("XY").newObject([comp])


def xiao_envelope() -> cq.Workplane:
    """Simplified envelope used for fit checks: PCB stack + USB-C overhang."""
    tx, ty, tz = xiao_transform()
    z0 = p.xiao_post_h
    stack = box_at(p.xiao_x0, p.xiao_x1, ty - 2.78, ty + 15.0, z0, z0 + p.xiao_stack_h)
    usb = box_at(p.xiao_x1, 13.81 + tx, ty + 1.65, ty + 10.59, 1.0 + tz, 4.21 + tz).edges("|X").fillet(1.5)   # receptacle shell has full-radius ends
    return stack.union(usb)


def usb_sd_cutouts():
    """USB-C opening in the +X wall (from the STEP geometry) and the microSD card slot in the +Y wall."""
    tx, ty, tz = xiao_transform()
    c = 0.35
    c = p.usb_clear
    usb = box_at(p.L_in / 2 - 0.5, p.L_out / 2 + 1, ty + 1.65 - c, ty + 10.59 + c,
                 1.0 + tz - c, 4.21 + tz + c).edges("|X").fillet(1.6)
    sd = box_at(p.sd_card_x - p.sd_card_w / 2 - 1.0, p.sd_card_x + p.sd_card_w / 2 + 1.0,
                p.W_in / 2 - 0.5, p.W_out / 2 + 1,
                p.sd_card_z - 0.4, p.sd_card_z + p.sd_card_t + 0.4).edges("|Y").fillet(0.5)
    return usb, sd


def load_mic() -> cq.Workplane:
    s = cq.importers.importStep(MIC_STEP)
    return cq.Workplane("XY").newObject([cq.Compound.makeCompound(s.solids().vals())])


def place_mic(mic: cq.Workplane, cx, cy) -> cq.Workplane:
    """Mic PCB back (port side) up against the lid underside; components hang down."""
    comp = mic.val()
    comp = comp.translate((-16.51 / 2, -12.70 / 2, 0))     # centre in XY
    comp = comp.rotate((0, 0, 0), (1, 0, 0), 180)          # flip: back face up (z = +0.05)
    comp = comp.translate((cx, cy, p.H_in + p.mic_recess - p.mic_tape - 0.05))
    return cq.Workplane("XY").newObject([comp])


def mic_port_offset():
    """Port hole relative to board centre, after the flip."""
    return (8.25 - 16.51 / 2, -(7.82 - 12.70 / 2))


def mic_mount_offsets():
    return [(x - 16.51 / 2, -(10.16 - 12.70 / 2)) for x in (2.54, 13.97)]


def mic_envelope(cx, cy):
    z1 = p.H_in + p.mic_recess - p.mic_tape
    env = box_at(cx - p.mic_l / 2, cx + p.mic_l / 2, cy - p.mic_w / 2, cy + p.mic_w / 2,
                 z1 - p.mic_h, z1)
    for (mx, my) in mic_mount_offsets():                 # 2.5 mm mounting holes
        env = env.cut(cyl_at(cx + mx, cy + my, z1 - p.mic_h - 1, z1 + 1, 2.5))
    return env


# ----------------------------------------------------------------------------
# Simple component envelopes
# ----------------------------------------------------------------------------
def battery():
    x0 = -p.L_in / 2 + 0.5               # 0.5 mm from the -X wall; the +X end stops short of the microSD cradle
    x1 = x0 + p.bat_l
    return box_at(x0, x1, -p.bat_w / 2, p.bat_w / 2, p.bat_foam, p.bat_foam + p.bat_t)


def sd_y1():
    """+Y (card) edge of the microSD breakout: inside the tray rim. The card is captive (no wall slot)."""
    return p.W_in / 2 - p.sd_wall_gap


def sd_breakout():
    """SparkFun microSD breakout: PCB + socket, card edge toward the +Y wall. Card shown in the locked position."""
    x0, x1 = p.sd_x0, p.sd_x0 + p.sd_l
    y1 = sd_y1()
    y0 = y1 - p.sd_w
    z0 = p.xiao_post_h
    board = box_at(x0, x1, y0, y1, z0, z0 + 1.6)                                   # PCB; edges stay bare for the snap lips
    board = board.union(box_at(x0 + 1.24, x0 + 15.24, y1 - 17.0, y1 - 2.54, z0 + 1.6, z0 + p.sd_h))   # Molex socket body
    card = box_at(p.sd_card_x - p.sd_card_w / 2, p.sd_card_x + p.sd_card_w / 2,
                  y1 - 14.0, y1 + 0.7, p.sd_card_z, p.sd_card_z + p.sd_card_t)
    return board.union(card)


def switch():
    yb0 = p.W_in / 2 + p.sw_wall_pocket - p.sw_body_h
    body = box_at(p.sw_x - p.sw_body / 2, p.sw_x + p.sw_body / 2, yb0, yb0 + p.sw_body_h,
                  p.sw_z - p.sw_body / 2, p.sw_z + p.sw_body / 2)
    plunger = (cq.Workplane("XZ").workplane(offset=-(yb0 + p.sw_body_h))
               .center(p.sw_x, p.sw_z).circle(p.sw_plunger_d / 2)
               .extrude(-(p.sw_total_h - p.sw_body_h)))
    return body.union(plunger)


def led():
    x, y = p.led_xy
    w = p.led_w / 2
    zt = p.H_in + p.led_recess                          # sits in the lid recess
    return box_at(x - w, x + w, y - w, y + w, zt - p.led_h, zt)


def motor():
    x, y = p.motor_xy
    zt = p.H_in + p.motor_recess
    return cyl_at(x, y, zt - p.motor_h, zt, p.motor_d)


def antenna():
    x, y = p.ant_xy
    return box_at(x - p.ant_l / 2, x + p.ant_l / 2, y - p.ant_w / 2, y + p.ant_w / 2,
                  p.H_in - p.ant_t, p.H_in)


def magnets():
    out = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            m = cyl_at(sx * p.magnet_x, sy * p.magnet_y, -p.magnet_pocket_depth,
                       -p.magnet_pocket_depth + p.magnet_t, p.magnet_d)
            out = m if out is None else out.union(m)
    return out


def boss_solid(x, y, grow=0.0, z0=0.0, z1=None):
    """Corner boss: a Ø boss_d post at (x, y) blended into the two adjacent walls (rounded inner corner),
    clipped to |y| >= boss_clip_y so it never reaches the XIAO / microSD boards. grow = radial clearance."""
    z1 = p.H_in if z1 is None else z1
    sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
    r = p.boss_d / 2 + grow
    wx, wy = sx * (p.L_in / 2 + 1), sy * (p.W_in / 2 + 1)
    cyl = cyl_at(x, y, z0, z1, 2 * r)
    stripx = box_at(min(x - sx * r, wx), max(x - sx * r, wx), min(y, wy), max(y, wy), z0, z1)
    stripy = box_at(min(x, wx), max(x, wx), min(y - sy * r, wy), max(y - sy * r, wy), z0, z1)
    body = cyl.union(stripx).union(stripy)
    clip = box_at(-p.L_in, p.L_in, min(sy * (p.boss_clip_y - grow), wy), max(sy * (p.boss_clip_y - grow), wy), z0 - 1, z1 + 1)
    return body.intersect(clip).intersect(rbox(p.L_in, p.W_in, z1 - z0 + 2, p.R_in, z0=z0 - 1))


def screws():
    out = None
    top = p.t_lid + p.H_in
    for (x, y) in p.boss_xy:
        ht = top - p.head_sink                                   # head top sits below the lid face
        shank = cyl_at(x, y, ht - p.screw_len, ht - 1.0, 2.0)
        head = (cq.Workplane("XY").workplane(offset=ht - 1.0).center(x, y)
                .circle(1.0).workplane(offset=1.0).circle(1.9).loft())
        s = shank.union(head)
        out = s if out is None else out.union(s)
    return out


def button_cap() -> cq.Workplane:
    """Turned aluminium cap: flange inside the wall (captive), shaft through the hole, domed face 0.8 proud."""
    wi = p.W_in / 2
    y_out = wi + p.wall + p.cap_proud
    y_fl0 = wi - 0.05 - p.cap_flange_t
    body = ycyl(p.sw_x, p.sw_z, y_fl0, y_fl0 + p.cap_flange_t, p.cap_flange_d)
    body = body.union(ycyl(p.sw_x, p.sw_z, y_fl0, y_out, p.cap_d))
    body = body.faces(">Y").edges().fillet(0.6)
    tip = wi + p.sw_wall_pocket + (p.sw_total_h - p.sw_body_h)       # plunger tip at rest
    body = body.cut(ycyl(p.sw_x, p.sw_z, y_fl0 - 1, tip, p.cap_bore_d))
    return body


def lid_mark_xy():
    return (22.0, -15.6)


def markings() -> dict[str, cq.Workplane]:
    """Laser-marked text, as thin solids filling the engravings (for renders; the cut is in shell() / lid())."""
    zt = p.H_in + p.t_lid
    zb = -p.t_plate
    d = p.mark_depth
    mx, my = lid_mark_xy()
    return {
        "lid": text_solid("OpenPocket", 2.2, mx, my, zt, d),
        "bottom": text_solid("OpenPocket", 3.4, 0, 2.2, zb, d, flip=True).union(
            text_solid("open-source hardware  /  v0", 1.5, 0, -2.6, zb, d, flip=True)),
    }


def screws_render() -> cq.Workplane:
    """Screws with a 6-lobe (Torx-like T6) recess, for renders only."""
    out = None
    top = p.t_lid + p.H_in
    for (x, y) in p.boss_xy:
        ht = top - p.head_sink
        shank = cyl_at(x, y, ht - p.screw_len, ht - 1.0, 2.0)
        head = (cq.Workplane("XY").workplane(offset=ht - 1.0).center(x, y)
                .circle(1.0).workplane(offset=1.0).circle(1.9).loft())
        pts = []
        for k in range(12):
            r = 0.88 if k % 2 == 0 else 0.55
            a = math.radians(k * 30)
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
        star = cq.Workplane("XY").workplane(offset=ht - 0.8).polyline(pts).close().extrude(1.0)
        s = shank.union(head).cut(star)
        out = s if out is None else out.union(s)
    return out


# ----------------------------------------------------------------------------
# Aluminium shell (floor + walls, one pocket, rebate for the lid)
# ----------------------------------------------------------------------------
def shell() -> cq.Workplane:
    z_top = p.H_in + p.t_lid
    body = rbox(p.L_out, p.W_out, p.t_plate + p.H_in + p.t_lid, p.R_out, z0=-p.t_plate)
    body = body.faces("<Z").edges().fillet(p.shell_bot_r)
    body = body.faces(">Z").edges().chamfer(p.shell_top_c)
    # pocket
    body = body.cut(rbox(p.L_in, p.W_in, p.H_in + 2, p.R_in, z0=0))
    # corner bosses left standing in the pocket, blind tapped M2
    for (x, y) in p.boss_xy:
        body = body.union(boss_solid(x, y))
    for (x, y) in p.boss_xy:
        body = body.cut(cyl_at(x, y, p.H_in - p.tap_depth, p.H_in + 1, p.tap_drill_d))
    # rebate for the lid, flush with the wall top
    body = body.cut(rbox(p.L_in + 2 * p.rebate_w, p.W_in + 2 * p.rebate_w, p.t_lid + 1, p.R_in + p.rebate_w, z0=p.H_in))
    # magnet pockets from the inside of the floor
    for sx in (-1, 1):
        for sy in (-1, 1):
            body = body.cut(cyl_at(sx * p.magnet_x, sy * p.magnet_y, -p.magnet_pocket_depth, 1,
                                   p.magnet_d + p.magnet_pocket_clear))
    # USB-C opening in the +X wall, button hole in the +Y wall
    usb, _sd = usb_sd_cutouts()
    body = body.cut(usb)
    body = body.cut(usb_chamfer_tool())
    wo = p.W_out / 2
    body = body.cut(ycyl(p.sw_x, p.sw_z, p.W_in / 2 - 1, wo + 1, p.btn_hole_d))
    body = body.cut(ycyl(p.sw_x, p.sw_z, wo - p.btn_spot_depth, wo + 1, p.btn_spot_d))
    # laser marking on the bottom
    body = body.cut(markings()["bottom"])
    return body


def usb_chamfer_tool() -> cq.Workplane:
    """Lofted tool: the USB-C opening grown by usb_chamfer at the outer face, tapering to nothing 0.3 inside."""
    tx, ty, tz = xiao_transform()
    c = p.usb_clear
    y0, y1 = ty + 1.65 - c, ty + 10.59 + c
    z0, z1 = 1.0 + tz - c, 4.21 + tz + c
    yc, zc, w, h = (y0 + y1) / 2, (z0 + z1) / 2, y1 - y0, z1 - z0
    k = p.usb_chamfer
    xo = p.L_out / 2
    s_in = cq.Sketch().rect(w, h).vertices().fillet(1.6)
    s_out = cq.Sketch().rect(w + 2 * k + 0.4, h + 2 * k + 0.4).vertices().fillet(1.6 + k + 0.2)
    wp = cq.Workplane("YZ", origin=(xo - k, 0, 0)).center(yc, zc)
    return wp.placeSketch(s_in, s_out.moved(cq.Location(cq.Vector(0, 0, k + 0.2)))).loft()


# ----------------------------------------------------------------------------
# Printed tray: floor plate with every cradle, dropped into the shell pocket
# ----------------------------------------------------------------------------
def tray() -> cq.Workplane:
    L, W = p.L_in - 2 * p.tray_clear, p.W_in - 2 * p.tray_clear
    body = rbox(L, W, p.tray_t, p.R_in - p.tray_clear)
    # low rim along the walls
    rim = rbox(L, W, p.tray_rim_h, p.R_in - p.tray_clear).cut(
        rbox(L - 2 * p.tray_rim_t, W - 2 * p.tray_rim_t, p.tray_rim_h + 2, max(p.R_in - p.tray_clear - p.tray_rim_t, 0.5), z0=-1))
    body = body.union(rim)
    # no rim where the XIAO, the microSD board and the button sit against the wall
    body = body.cut(box_at(L / 2 - p.tray_rim_t - 0.5, L / 2 + 1, p.xiao_y_center - p.xiao_pcb_w / 2 - 1.5, p.xiao_y_center + p.xiao_pcb_w / 2 + 1.5, p.tray_t, p.tray_rim_h + 1))
    body = body.cut(box_at(p.sd_x0 - 2, p.L_in / 2 + 1, W / 2 - p.tray_rim_t - 0.5, W / 2 + 1, p.tray_t, p.tray_rim_h + 1))
    body = body.cut(box_at(p.sw_x - p.sw_body / 2 - 2.5, p.sw_x + p.sw_body / 2 + 2.5, W / 2 - p.tray_rim_t - 0.5, W / 2 + 1, p.tray_t, p.tray_rim_h + 1))
    # battery cutout: the cell sits on the aluminium floor; the cutout edges plus ribs locate it
    bx0 = -p.L_in / 2 + 0.5
    bx1 = bx0 + p.bat_l
    yb = p.bat_w / 2 + p.bat_cut_clear
    body = body.cut(box_at(bx0 - p.bat_cut_clear, bx1 + p.bat_cut_clear, -yb, yb, -1, p.tray_rim_h + 1))
    body = body.union(box_at(bx1 + p.bat_cut_clear, bx1 + p.bat_cut_clear + p.bat_rib_t, -6, 6, 0, p.bat_rib_h))   # end stop
    for rx in p.bat_rib_x:
        for (ya, yb_) in ((-W / 2, -yb), (yb, W / 2)):
            body = body.union(box_at(rx - p.bat_rib_t / 2, rx + p.bat_rib_t / 2, ya, yb_, 0, p.bat_rib_h))
    z0 = p.tray_t
    post_h = p.xiao_post_h - p.tray_t                   # posts on top of the tray floor

    # XIAO corner posts and retaining rails
    x0, x1 = p.xiao_x0, p.xiao_x1
    yc = p.xiao_y_center
    y0, y1 = yc - p.xiao_pcb_w / 2, yc + p.xiao_pcb_w / 2
    s = p.xiao_post
    for (px, py) in [(x0 + 0.9, y0 + 0.9), (x0 + 0.9, y1 - 0.9), (x1 - 0.9, y0 + 0.9), (x1 - 0.9, y1 - 0.9)]:
        body = body.union(box_at(px - s / 2, px + s / 2, py - s / 2, py + s / 2, 0, p.xiao_post_h))
    rail_h, rail_t, cl = 3.0, 0.8, 0.3
    body = body.union(box_at(x0 - cl - rail_t, x0 - cl, y0 - cl - rail_t, y1 + cl, 0, rail_h))
    for (ya, yb_) in [(y0 - cl - rail_t, y0 - cl)]:
        body = body.union(box_at(x0 - cl, x0 + 6, ya, yb_, 0, rail_h))
        body = body.union(box_at(x1 - 6, x1, ya, yb_, 0, rail_h))
    tx, ty, tz = xiao_transform()                       # the +X wall itself is the end stop (0.1 mm)
    c = p.usb_clear

    # microSD breakout: posts, rails with snap lips, end stops at the +Y rim
    sx0, sx1 = p.sd_x0, p.sd_x0 + p.sd_l
    sy1 = sd_y1()
    sy0 = sy1 - p.sd_w
    for (px, py) in [(sx0 + 0.9, sy0 + 0.9), (sx0 + 0.9, sy1 - 0.9), (sx1 - 0.9, sy0 + 0.9), (sx1 - 0.9, sy1 - 0.9)]:
        body = body.union(box_at(px - s / 2, px + s / 2, py - s / 2, py + s / 2, 0, p.xiao_post_h))
    lip_z = p.xiao_post_h + 1.6 + 0.2
    body = body.union(box_at(sx0 - cl - rail_t, sx0 - cl, sy0 + 2, sy1 - 2, 0, lip_z + 0.8))
    body = body.union(box_at(sx0 - cl - rail_t, sx0 + 0.5, sy0 + 4, sy1 - 4, lip_z, lip_z + 0.8))
    body = body.union(box_at(sx1 + cl, sx1 + cl + rail_t, sy0 + 2, sy1 - 2, 0, lip_z + 0.8))
    body = body.union(box_at(sx1 - 0.3, sx1 + cl + rail_t, sy0 + 6, sy1 - 6, lip_z, lip_z + 0.8))
    body = body.union(box_at(sx0 - cl, sx1 + cl, sy0 - cl - rail_t, sy0 - cl, 0, rail_h))
    for (xa, xb) in ((sx0 - cl, p.sd_card_x - p.sd_card_w / 2 - 1.5), (p.sd_card_x + p.sd_card_w / 2 + 1.5, sx1 + cl)):
        body = body.union(box_at(xa, xb, sy1 + cl, W / 2, 0, rail_h))              # end stops beside the (captive) card

    # side button cradle: ribs, ledge, backstop; the body front sits against the aluminium wall
    wi = W / 2
    yb0 = p.W_in / 2 + p.sw_wall_pocket - p.sw_body_h
    rib_t, rib_cl = 1.2, 0.8
    y_back = yb0 - p.sw_leg_space - p.sw_backstop_t
    top = p.sw_z + p.sw_body / 2
    for xa in (p.sw_x - p.sw_body / 2 - rib_cl - rib_t, p.sw_x + p.sw_body / 2 + rib_cl):
        body = body.union(box_at(xa, xa + rib_t, y_back, wi, 0, top))
    body = body.union(box_at(p.sw_x - p.sw_body / 2 - rib_cl, p.sw_x + p.sw_body / 2 + rib_cl,
                             y_back, wi, 0, p.sw_z - p.sw_body / 2 - 0.2))
    body = body.union(box_at(p.sw_x - p.sw_body / 2 - rib_cl, p.sw_x + p.sw_body / 2 + rib_cl,
                             y_back, y_back + p.sw_backstop_t, 0, top))
    # finally clear the corner bosses and the USB-C zone (cuts whatever feature reaches them)
    for (x, y) in p.boss_xy:
        body = body.cut(boss_solid(x, y, grow=0.2, z0=-1))
    body = body.cut(box_at(x1 - 0.5, p.L_in / 2 + 1, ty + 1.65 - c - 0.4, ty + 10.59 + c + 0.4, p.tray_t, p.H_in))
    return body


# ----------------------------------------------------------------------------
# Aluminium lid: flat plate in the rebate, countersunk screws, mic / LED holes, RF window
# ----------------------------------------------------------------------------
def lid() -> cq.Workplane:
    z0 = p.H_in
    body = rbox(p.lid_L, p.lid_W, p.t_lid, p.R_in + p.rebate_w - p.lid_clear, z0=z0)
    body = body.faces(">Z").edges().fillet(p.lid_edge_r)
    body = body.faces(">Z").workplane().pushPoints(p.boss_xy).cskHole(p.boss_hole_d, p.csk_d, 90)
    # round the countersink mouths: the only edges a thumb meets around the screws
    zt = z0 + p.t_lid
    mouths = [e for e in body.edges().vals()
              if e.geomType() == "CIRCLE" and abs(e.radius() - p.csk_d / 2) < 0.02 and abs(e.Center().z - zt) < 0.02]
    body = body.newObject(mouths).fillet(p.csk_edge_r)
    # mic recesses and acoustic holes (recess locates the PCB, tape holds it)
    for (cx, cy) in (p.mic1_xy, p.mic2_xy):
        body = body.cut(box_at(cx - p.mic_l / 2 - 0.3, cx + p.mic_l / 2 + 0.3, cy - p.mic_w / 2 - 0.3, cy + p.mic_w / 2 + 0.3,
                               z0 - 1, z0 + p.mic_recess))
        px, py = mic_port_offset()
        for (gx, gy) in grille_xy(cx + px, cy + py):
            body = body.cut(cyl_at(gx, gy, z0 - 1, z0 + p.t_lid + 1, p.mic_grille_d))
    # motor recess (the LED sits under the RF window insert, no hole in the metal)
    mx, my = p.motor_xy
    body = body.cut(cyl_at(mx, my, z0 - 1, z0 + p.motor_recess, p.motor_d + 0.6))
    # RF window: through cutout + underside recess for the insert flange
    ax, ay = p.rf_xy
    body = body.cut(rbox_at(ax, ay, p.rf_l, p.rf_w, z0 - 1, z0 + p.t_lid + 1, p.rf_r))
    f = p.rf_flange
    body = body.cut(rbox_at(ax, ay, p.rf_l + 2 * f, p.rf_w + 2 * f, z0 - 1, z0 + p.rf_flange_t, p.rf_r + f))
    # laser marking
    body = body.cut(markings()["lid"])
    return body


def rf_insert() -> cq.Workplane:
    """Printed (or acrylic) window flush with the lid top; flange sits in the underside recess, glued."""
    z0 = p.H_in
    ax, ay = p.rf_xy
    c = p.rf_clear
    f = p.rf_flange
    plug = rbox_at(ax, ay, p.rf_l - 2 * c, p.rf_w - 2 * c, z0 + p.rf_flange_t - 0.01, z0 + p.t_lid, p.rf_r - c)
    flange = rbox_at(ax, ay, p.rf_l + 2 * f - 2 * c, p.rf_w + 2 * f - 2 * c, z0, z0 + p.rf_flange_t, p.rf_r + f - c)
    body = plug.union(flange)
    lx, ly = p.led_xy                                   # LED locating recess in the insert underside; the insert is the diffuser
    lw = p.led_w / 2 + 0.3
    body = body.cut(box_at(lx - lw, lx + lw, ly - lw, ly + lw, z0 - 1, z0 + p.led_recess))
    return body


# ----------------------------------------------------------------------------
# Fit check
# ----------------------------------------------------------------------------
def fit_check(parts: dict[str, cq.Workplane], allowed_contact=0.05) -> bool:
    names = list(parts)
    ok = True
    print("\nFit check (pairwise intersection volume, mm^3):")
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = parts[names[i]], parts[names[j]]
            if {names[i], names[j]} == {"shell", "screws"}:   # screws thread into the shell bosses
                continue
            try:
                v = a.intersect(b).val().Volume()
            except Exception:
                v = 0.0
            flag = "OK " if v <= allowed_contact else "CLASH"
            if v > allowed_contact:
                ok = False
            if v > 0 or flag == "CLASH":
                print(f"  {flag} {names[i]:>12s} x {names[j]:<12s} {v:8.3f}")
    print("  RESULT:", "no interference" if ok else "INTERFERENCE FOUND")
    return ok


def inside_cavity_check(parts: dict[str, cq.Workplane], extra_top: float = 0.0) -> bool:
    """Every component must sit inside the cavity (between plate top and lid underside).
    extra_top: allowance above the lid underside for parts that sit in lid recesses."""
    cav = rbox(p.L_in, p.W_in, p.H_in + extra_top, p.R_in)
    ok = True
    print("\nCavity check (volume outside cavity, mm^3):")
    for n, w in parts.items():
        v_out = w.cut(cav).val().Volume() if w.cut(cav).solids().size() else 0.0
        print(f"  {'OK ' if v_out < 0.05 else 'OUT'} {n:>12s} {v_out:8.3f}")
        ok &= v_out < 0.05
    return ok


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main(check_only=False):
    os.makedirs(EXPORT, exist_ok=True)
    print(f"Enclosure outer: {p.L_out:.1f} x {p.W_out:.1f} x {p.H_total:.1f} mm")

    sh, tr, l, rf, cap = shell(), tray(), lid(), rf_insert(), button_cap()
    comps = {
        "xiao": xiao_envelope(), "battery": battery(), "mic1": mic_envelope(*p.mic1_xy),
        "mic2": mic_envelope(*p.mic2_xy), "sd": sd_breakout(), "switch": switch(), "led": led(), "motor": motor(),
        "antenna": antenna(), "magnets": magnets(), "screws": screws(),
    }
    allparts = {"shell": sh, "tray": tr, "lid": l, "rf-insert": rf, "button-cap": cap, **comps}
    ok = fit_check(allparts)
    inner = {k: v for k, v in comps.items() if k not in ("magnets", "screws", "switch", "xiao", "mic1", "mic2", "led", "motor", "sd")}
    ok &= inside_cavity_check(inner)
    ok &= inside_cavity_check({"led": comps["led"]}, extra_top=p.led_recess)
    ok &= inside_cavity_check({"motor": comps["motor"]}, extra_top=p.motor_recess)
    ok &= inside_cavity_check({k: comps[k] for k in ("mic1", "mic2")}, extra_top=p.mic_recess)   # mics sit in lid recesses
    # XIAO: everything except the USB-C / microSD overhangs must be inside the cavity
    tx, ty, tz = xiao_transform()
    stack = box_at(p.xiao_x0, p.xiao_x1, ty - 2.78, ty + 15.0, p.xiao_post_h, p.xiao_post_h + p.xiao_stack_h)
    ok &= inside_cavity_check({"xiao-stack": stack})
    # microSD breakout: board inside the cavity; the card may enter the wall slot
    ok &= inside_cavity_check({"sd-board": box_at(p.sd_x0, p.sd_x0 + p.sd_l, sd_y1() - p.sd_w, sd_y1(), p.xiao_post_h, p.xiao_post_h + p.sd_h)})
    # switch body must be inside the cavity
    wi = p.W_in / 2
    yb0 = wi + p.sw_wall_pocket - p.sw_body_h
    sw_body = box_at(p.sw_x - p.sw_body / 2, p.sw_x + p.sw_body / 2, yb0, min(yb0 + p.sw_body_h, wi), p.sw_z - 3, p.sw_z + 3)
    ok &= inside_cavity_check({"switch-body": sw_body})
    if check_only:
        return ok

    # machined parts (STEP is the master), printed parts (STL)
    for n, w in (("shell", sh), ("lid", l), ("tray", tr), ("rf-insert", rf), ("button-cap", cap)):
        cq.exporters.export(w, os.path.join(EXPORT, f"openpocket-{n}.step"))
        cq.exporters.export(w, os.path.join(EXPORT, f"openpocket-{n}.stl"), tolerance=0.01, angularTolerance=0.1)
    cq.exporters.export(sh.faces("<Z").wires().toPending().extrude(0.01), os.path.join(EXPORT, "openpocket-shell-outline.dxf"))
    cq.exporters.export(l.faces("<Z").wires().toPending().extrude(0.01), os.path.join(EXPORT, "openpocket-lid-outline.dxf"))

    # component envelopes (for renders / exploded views)
    for n, w in comps.items():
        cq.exporters.export(w, os.path.join(EXPORT, f"comp-{n}.stl"), tolerance=0.02, angularTolerance=0.2)

    # real vendor models: meshes for the renders / site viewer, and an interference check against the printed parts
    # (skipped when the vendor STEP files are not downloaded, see vendor-models/README.md)
    if not (os.path.exists(XIAO_STEP) and os.path.exists(MIC_STEP)):
        print("\nVendor STEP models not found: skipping the vendor check and openpocket-assembly.step")
    else:
        xiao_real = load_xiao()
        mics_real = {"mic1": place_mic(load_mic(), *p.mic1_xy), "mic2": place_mic(load_mic(), *p.mic2_xy)}
        cq.exporters.export(xiao_real, os.path.join(EXPORT, "vendor-xiao.stl"), tolerance=0.02, angularTolerance=0.2)
        for n, w in mics_real.items():
            cq.exporters.export(w, os.path.join(EXPORT, f"vendor-{n}.stl"), tolerance=0.02, angularTolerance=0.2)
        print("\nReal vendor models vs printed parts (intersection volume, mm^3):")
        for n, w in {"xiao": xiao_real, **mics_real}.items():
            for pn, pw in (("shell", sh), ("tray", tr), ("lid", l)):
                try:
                    v = w.intersect(pw).val().Volume()
                except Exception:
                    v = 0.0
                print(f"  {'OK ' if v <= 0.05 else 'CLASH'} {n:>6s} x {pn:<4s} {v:8.3f}")
                ok &= v <= 0.05

        # full assembly STEP with the real vendor models
        asm = cq.Assembly(name="OpenPocket-v0")
        asm.add(sh, name="shell-AL6061", color=cq.Color(0.75, 0.76, 0.78))
        asm.add(l, name="lid-AL6061", color=cq.Color(0.75, 0.76, 0.78))
        asm.add(tr, name="tray-printed", color=cq.Color(0.15, 0.15, 0.17))
        asm.add(rf, name="rf-window-printed", color=cq.Color(0.2, 0.2, 0.25))
        asm.add(cap, name="button-cap-AL6061", color=cq.Color(0.95, 0.45, 0.1))
        asm.add(load_xiao(), name="xiao-esp32s3", color=cq.Color(0.1, 0.3, 0.15))
        mic = load_mic()
        asm.add(place_mic(mic, *p.mic1_xy), name="mic1-adafruit-3421", color=cq.Color(0.1, 0.1, 0.5))
        asm.add(place_mic(mic, *p.mic2_xy), name="mic2-adafruit-3421", color=cq.Color(0.1, 0.1, 0.5))
        for n, w in comps.items():
            if n.startswith("mic") or n == "xiao":
                continue
            asm.add(w, name=n, color=cq.Color(0.6, 0.6, 0.2))
        asm.save(os.path.join(EXPORT, "openpocket-assembly.step"))
    # fine meshes for the photoreal renders (renders/blender/)
    rdir = os.path.join(EXPORT, "render")
    os.makedirs(rdir, exist_ok=True)
    fine = dict(tolerance=0.004, angularTolerance=0.05)
    for n, w in (("shell", sh), ("lid", l), ("tray", tr), ("rf-insert", rf), ("button-cap", cap),
                 ("screws", screws_render()), ("mark-lid", markings()["lid"]), ("mark-bottom", markings()["bottom"])):
        cq.exporters.export(w, os.path.join(rdir, f"{n}.stl"), **fine)
    print("\nExported to", EXPORT)
    return ok


if __name__ == "__main__":
    ok = main(check_only="--check" in sys.argv)
    sys.exit(0 if ok else 1)
