"""Manufacturing drawings for the two machined aluminium parts: shell (OP0-MECH-003) and lid (OP0-MECH-011).

Run: ../../../.venv/bin/python enclosure_drawings.py  -> shell-drawing.pdf/.png, lid-drawing.pdf/.png
All dimensions come from the CAD parameters so the drawings cannot drift from the STEP files.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cad"))
from openpocket_cad import p, mic_port_offset, grille_xy, lid_mark_xy  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATE = "2026-10-19"


def hdim(ax, x0, x1, y, text, off=0):
    ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((x0 + x1) / 2, y + 0.8 + off, text, ha="center", va="bottom", fontsize=9)


def vdim(ax, x, y0, y1, text):
    ax.annotate("", xy=(x, y0), xytext=(x, y1), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(x + 0.8, (y0 + y1) / 2, text, ha="left", va="center", fontsize=9, rotation=90)


def rrect(ax, cx, cy, l, w, r, **kw):
    ax.add_patch(FancyBboxPatch((cx - l / 2 + r, cy - w / 2 + r), l - 2 * r, w - 2 * r,
                                boxstyle=f"round,pad={r}", **kw))


RFQ_REF = "OP0-RFQ-001"
RENDERS = os.path.join(HERE, "..", "renders")


def sheet(title, partno, notes, draw_views, render_png=None):
    fig = plt.figure(figsize=(16.5, 11.7))      # A3 landscape
    ax = fig.add_axes([0.03, 0.36, 0.62, 0.60])
    ax2 = fig.add_axes([0.03, 0.05, 0.62, 0.26])
    for a in (ax, ax2):
        a.set_aspect("equal")
        a.axis("off")
    draw_views(ax, ax2)
    tx = 0.68
    fig.text(tx, 0.93, title, fontsize=16, weight="bold")
    fig.text(tx, 0.905, f"Part no. {partno}    Rev B    Sheet 1/1    RFQ ref. {RFQ_REF}", fontsize=10)
    for i, n in enumerate(notes):
        fig.text(tx, 0.86 - i * 0.022, n, fontsize=8.6)
    if render_png and os.path.exists(render_png):
        axr = fig.add_axes([0.70, 0.08, 0.27, 0.27])
        axr.imshow(plt.imread(render_png))
        axr.axis("off")
        axr.set_title("Isometric reference (not to scale)", fontsize=8, color="#444", loc="left")
    fig.text(tx, 0.045, "OpenPocket, open-source hardware (CERN-OHL-P v2). Contact on the cover sheet.", fontsize=8.5, color="#444")
    fig.text(tx, 0.025, f"Date: {DATE}. STEP file governs; this sheet carries tolerances, threads and finish.", fontsize=8.5, color="#444")
    return fig


def cover_sheet():
    """One-page RFQ cover: what is in the package, quantities, finishes, questions, contact."""
    fig = plt.figure(figsize=(8.27, 11.69))     # A4 portrait
    lines = [
        ("OpenPocket v0 — RFQ: two machined aluminium parts", 15, True),
        (f"RFQ ref. {RFQ_REF}    Date {DATE}    Open-source hardware project, CERN-OHL-P v2", 9, False),
        ("", 6, False),
        ("PARTS (one set = 1 shell + 1 lid; they are assembled together, please quote as a set and per part)", 10, True),
        (f"1. OP0-MECH-003  Shell   6061-T6 from solid, {L:.1f} x {W:.1f} x {Hs:.1f} mm, ~39 g. One pocket {Li:.1f} x {Wi:.1f} x {p.H_in:.1f},", 9, False),
        (f"   four Ø{p.boss_d:.1f} corner bosses with blind M2x0.4, lid rebate {rl:.1f} x {rw:.1f} x {p.t_lid:.1f}, 4 magnet pockets Ø{md:.1f} x {mdep:.1f} in the floor,", 9, False),
        (f"   USB-C opening 9.5 x 3.8 (R1.6, C{p.usb_chamfer:.1f} outside) through one end wall, Ø{p.btn_hole_d:.1f} + spot face Ø{p.btn_spot_d:.1f} through one side wall.", 9, False),
        (f"2. OP0-MECH-011  Lid     6061-T6 plate, {lL:.1f} x {lW:.1f} x {p.t_lid:.1f} mm, ~16 g. Four Ø{p.boss_hole_d:.1f} thru, 90° csk Ø{p.csk_d:.1f}, R{p.csk_edge_r:.1f} mouths;", 9, False),
        (f"   two 7-hole Ø{p.mic_grille_d:.1f} grilles, one {p.rf_l:.0f} x {p.rf_w:.0f} R{p.rf_r:.0f} thru window; three shallow recesses from the underside; laser mark.", 9, False),
        (f"3. OP0-MECH-012  Button cap (optional, please quote if you turn parts): 6061, Ø{p.cap_flange_d:.1f} x 3.4 mm, orange anodize. STEP only.", 9, False),
        ("", 6, False),
        ("FILES IN THIS PACKAGE", 10, True),
        ("   openpocket-shell.step, openpocket-lid.step   (AP214, masters; they govern if anything conflicts)", 9, False),
        ("   shell-drawing.pdf, lid-drawing.pdf           (A3, tolerances, threads, finish, notes)", 9, False),
        ("   openpocket-shell-outline.dxf, openpocket-lid-outline.dxf   (2D outlines, convenience only)", 9, False),
        ("   render-assembled.png, render-exploded.png    (what the parts are for)", 9, False),
        ("", 6, False),
        ("QUANTITIES TO QUOTE", 10, True),
        ("   1 / 10 / 100 / 1000 sets, each as a separate line: unit price per part, setup / NRE, lead time.", 9, False),
        ("   One set now for a functional test; target production run ~1000 sets. Please state your monthly capacity", 9, False),
        ("   and the lead time for a 1000-set order (one batch or releases).", 9, False),
        ("", 6, False),
        ("FINISH (quote each option)", 10, True),
        ("   (a) bead blast + black anodize Type II;  (b) bead blast + clear anodize Type II;  (c) as machined, deburred.", 9, False),
        ("   Threads masked for anodize or chased after. Both parts in the same anodize batch.", 9, False),
        ("", 6, False),
        ("TOLERANCES (summary; full callouts on the drawings)", 10, True),
        ("   ±0.1 general. Pocket, rebate and lid outline ±0.05 (the lid sits flush in the rebate with 0.1 per side).", 9, False),
        ("   Recess depths ±0.05. Flatness 0.1. Ra 1.6 µm on outside faces.", 9, False),
        ("", 6, False),
        ("PLEASE TELL US", 10, True),
        ("   - price per part at each quantity, NRE, lead time, shipping to the USA (San Francisco) and to Poland;", 9, False),
        ("   - whether STEP only is enough for you or you need the 2D drawings;", 9, False),
        ("   - anything in the design that makes the parts more expensive than they need to be (for example the blind M2", 9, False),
        ("     threads, the 0.9 mm floor under the magnet pockets, the side openings, the two-sided lid). We will change it.", 9, False),
        ("", 6, False),
        ("CONTACT", 10, True),
        ("   [name]  —  [email]  —  [phone]", 9, False),
        ("   Open-source project; files may be shared with your machinists freely. No NDA needed.", 9, False),
    ]
    y = 0.95
    for text, size, bold in lines:
        fig.text(0.06, y, text, fontsize=size, weight="bold" if bold else "normal", family="DejaVu Sans")
        y -= 0.0115 * (size / 9) + (0.008 if text == "" else 0.012)
    return fig


# ----------------------------------------------------------------------------
# Shell
# ----------------------------------------------------------------------------
L, W, R = p.L_out, p.W_out, p.R_out
Li, Wi, Ri = p.L_in, p.W_in, p.R_in
Hs = p.t_plate + p.H_in + p.t_lid
md = p.magnet_d + p.magnet_pocket_clear
mdep = p.magnet_pocket_depth
bx, by = p.boss_xy[3]
rl, rw = Li + 2 * p.rebate_w, Wi + 2 * p.rebate_w


def shell_views(ax, ax2):
    ax.set_title("TOP VIEW (open side), scale 1:1 at A3", loc="left", fontsize=10)
    rrect(ax, 0, 0, L, W, R, fc="white", ec="k", lw=1.4)
    rrect(ax, 0, 0, rl, rw, Ri + p.rebate_w, fc="#f2f2f2", ec="k", lw=0.8, ls="--")
    rrect(ax, 0, 0, Li, Wi, Ri, fc="white", ec="k", lw=1.0)
    for (x, y) in p.boss_xy:
        ax.add_patch(Circle((x, y), p.boss_d / 2, fc="#dddddd", ec="k", lw=0.9))
        ax.add_patch(Circle((x, y), p.tap_drill_d / 2, fc="white", ec="k", lw=0.8))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(Circle((sx * p.magnet_x, sy * p.magnet_y), md / 2, fc="white", ec="k", lw=1.0))
    # USB-C opening on the +X wall (shown as hidden lines), button hole on the +Y wall
    ax.plot([L / 2 - 0.3, L / 2 - 0.3], [-14.1, -5.2], "k:", lw=0.8)
    ax.text(L / 2 + 15, -9.6, "USB-C opening\n9.5 x 3.8 R1.6\nz 2.0..5.8 above floor", fontsize=7.5, va="center")
    ax.plot([p.sw_x - 2.1, p.sw_x + 2.1], [W / 2 + 0.3, W / 2 + 0.3], "k:", lw=1.5)
    ax.text(p.sw_x, W / 2 + 2.5, f"Ø{p.btn_hole_d:.1f} THRU wall + spot face Ø{p.btn_spot_d:.1f} ↓{p.btn_spot_depth:.1f}, z {p.sw_z:.1f} above floor", fontsize=7.5, ha="center")
    ax.plot([-L / 2 - 2, L / 2 + 2], [0, 0], color="#888", lw=0.5, ls="-.")
    ax.plot([0, 0], [-W / 2 - 2, W / 2 + 2], color="#888", lw=0.5, ls="-.")
    hdim(ax, -L / 2, L / 2, W / 2 + 7, f"{L:.1f}")
    hdim(ax, -Li / 2, Li / 2, -W / 2 - 7, f"{Li:.1f} pocket")
    hdim(ax, -rl / 2, rl / 2, -W / 2 - 12, f"{rl:.1f} rebate")
    hdim(ax, -p.magnet_x, p.magnet_x, -W / 2 - 17, f"{2 * p.magnet_x:.1f}")
    vdim(ax, L / 2 + 6, -W / 2, W / 2, f"{W:.1f}")
    vdim(ax, -L / 2 - 6, -Wi / 2, Wi / 2, f"{Wi:.1f} pocket")
    vdim(ax, -L / 2 - 11, -rw / 2, rw / 2, f"{rw:.1f} rebate")
    vdim(ax, -L / 2 - 16, -p.magnet_y, p.magnet_y, f"{2 * p.magnet_y:.1f}")
    hdim(ax, -bx, bx, W / 2 + 12, f"{2 * bx:.1f}")
    vdim(ax, L / 2 + 11, -by, by, f"{2 * by:.1f}")
    ax.annotate(f"4x M2x0.4 blind, drill Ø{p.tap_drill_d} x {p.tap_depth:.1f} deep, thread 5.0 min", xy=(bx, by), xytext=(bx - 30, W / 2 + 19),
                fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.annotate(f"4x Ø{md:.1f} +0.1/-0 POCKET ↓{mdep:.1f} in the floor", xy=(p.magnet_x, p.magnet_y), xytext=(p.magnet_x - 40, W / 2 + 25),
                fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.text(-L / 2 - 18, -W / 2 - 21, f"R{R:.0f} x4 outside, R{Ri:.1f} x4 pocket (Ø6 end mill), R{Ri + p.rebate_w:.1f} rebate", fontsize=8.5)
    ax.set_xlim(-L / 2 - 20, L / 2 + 30)
    ax.set_ylim(-W / 2 - 22, W / 2 + 30)

    # section A-A through the magnet pockets and a boss (y = +21 / +13 combined schematic)
    ax2.set_title("SECTION A-A (along X through a boss row and the magnet pockets), scale 2:1", loc="left", fontsize=10)
    s = 2.0
    X0 = -L / 2 * s
    floor = p.t_plate
    # outer profile
    prof = [(-L / 2, -floor), (L / 2, -floor), (L / 2, p.H_in + p.t_lid), (L / 2 - 0.8, p.H_in + p.t_lid), (L / 2 - 0.8, p.H_in),
            (Li / 2, p.H_in), (Li / 2, 0), (-Li / 2, 0), (-Li / 2, p.H_in), (-L / 2 + 0.8, p.H_in), (-L / 2 + 0.8, p.H_in + p.t_lid),
            (-L / 2, p.H_in + p.t_lid)]
    ax2.add_patch(Polygon([(x * s, z * s) for x, z in prof], closed=True, fc="#e8e8e8", ec="k", lw=1.2, hatch="///"))
    for sx in (-1, 1):
        ax2.add_patch(Rectangle(((sx * p.magnet_x - md / 2) * s, -mdep * s), md * s, mdep * s, fc="white", ec="k", lw=1.0))
    hdim(ax2, -L / 2 * s, L / 2 * s, (p.H_in + p.t_lid + 3) * s, f"{L:.1f}")
    vdim(ax2, (L / 2 + 3) * s, -floor * s, (p.H_in + p.t_lid) * s, f"{Hs:.1f}")
    vdim(ax2, (L / 2 + 8) * s, 0, p.H_in * s, f"{p.H_in:.1f} pocket depth")
    vdim(ax2, (L / 2 + 13) * s, p.H_in * s, (p.H_in + p.t_lid) * s, f"{p.t_lid:.1f} rebate")
    vdim(ax2, (-L / 2 - 3) * s, -floor * s, 0, f"{floor:.1f} floor")
    ax2.text(-L / 2 * s, (-floor - 4) * s, f"Walls {p.wall:.1f} (rebate leaves {p.wall - p.rebate_w:.1f} outside the lid). "
             f"Pocket floor to rebate {p.H_in:.1f} ±0.05.\nMagnet pockets ↓{mdep:.1f} leave {floor - mdep:.1f} floor. "
             f"R{p.shell_bot_r:.1f} round on the bottom outer edge, C{p.shell_top_c:.1f} bright-cut chamfer on the top outer edge.", fontsize=8.5, va="top")
    ax2.set_xlim((-L / 2 - 8) * s, (L / 2 + 20) * s)
    ax2.set_ylim((-floor - 10) * s, (p.H_in + p.t_lid + 6) * s)


shell_notes = [
    "MATERIAL: Aluminium 6061-T6, from solid.",
    f"OVERALL: {L:.1f} x {W:.1f} x {Hs:.1f} mm, outer corners R{R:.0f}.",
    f"POCKET: {Li:.1f} x {Wi:.1f} ±0.05, depth {p.H_in:.1f} ±0.05 from the rebate floor,",
    f"   corner R{Ri:.1f}; 4 corner bosses Ø{p.boss_d:.1f} blended into the walls, flat inner face at |Y| = {p.boss_clip_y:.1f}.",
    f"REBATE: {rl:.1f} x {rw:.1f} +0.05/-0, depth {p.t_lid:.1f} +0/-0.05 from the top face,",
    f"   corner R{Ri + p.rebate_w:.1f}. The lid (OP0-MECH-011) sits flush in it.",
    f"THREADS: 4x M2x0.4 blind in the bosses, drill Ø{p.tap_drill_d} x {p.tap_depth:.1f}, thread 5.0 min,",
    "   from the top. Do NOT break through the floor. Mask for anodize or chase after.",
    f"MAGNET POCKETS: 4x Ø{md:.1f} +0.1/-0, depth {mdep:.1f} ±0.05 from the pocket floor,",
    f"   flat bottom, floor left {p.t_plate - mdep:.1f}. Position ±0.05.",
    f"OPENINGS: USB-C 9.5 x 3.8 R1.6 ends, C{p.usb_chamfer:.1f} x 45° outside, through the +X wall;",
    f"   Ø{p.btn_hole_d:.1f} through the +Y wall with a spot face Ø{p.btn_spot_d:.1f} ↓{p.btn_spot_depth:.1f}. Positions per STEP, ±0.1.",
    "TOLERANCES (unless noted): ±0.1 linear; bottom flatness 0.1; walls 1.8 ±0.1.",
    f"EDGES: R{p.shell_bot_r:.1f} round bottom outer edge; C{p.shell_top_c:.1f} x 45° top outer edge, cut after",
    "   anodizing (bright edge) if you offer it, else before. Break the rest 0.2 max.",
    f"MARKING: laser mark on the bottom face (text in STEP, ↓{p.mark_depth:.2f}), after anodizing.",
    "SURFACE: Ra 1.6 µm or better on all outside faces (visible product).",
    "FINISH: (a) bead blast + black anodize Type II; (b) bead blast + clear",
    "   anodize; (c) as machined. Quote each. Mask the threads.",
    "QUANTITY FOR QUOTE: 1 / 10 / 100 / 1000 pcs, together with OP0-MECH-011 (lid).",
    "   1 pc now for testing, ~1000 target. State lead time, capacity, shipping PL / USA.",
    "FILES: openpocket-shell.step (master) + this PDF. STEP governs if in conflict.",
    "ALL DIMENSIONS IN MILLIMETRES. Third-angle projection.",
]

# ----------------------------------------------------------------------------
# Lid
# ----------------------------------------------------------------------------
lL, lW, lR = p.lid_L, p.lid_W, p.R_in + p.rebate_w - p.lid_clear


def lid_views(ax, ax2):
    ax.set_title("TOP VIEW (outside face), scale 1:1 at A3. Underside features shown dashed.", loc="left", fontsize=10)
    rrect(ax, 0, 0, lL, lW, lR, fc="white", ec="k", lw=1.4)
    for (x, y) in p.boss_xy:
        ax.add_patch(Circle((x, y), p.csk_d / 2, fc="white", ec="k", lw=0.9))
        ax.add_patch(Circle((x, y), p.boss_hole_d / 2, fc="white", ec="k", lw=0.8))
    px, py = mic_port_offset()
    for (cx, cy) in (p.mic1_xy, p.mic2_xy):
        ax.add_patch(Rectangle((cx - p.mic_l / 2 - 0.3, cy - p.mic_w / 2 - 0.3), p.mic_l + 0.6, p.mic_w + 0.6, fc="none", ec="k", lw=0.7, ls="--"))
        for (gx, gy) in grille_xy(cx + px, cy + py):
            ax.add_patch(Circle((gx, gy), p.mic_grille_d / 2, fc="white", ec="k", lw=0.6))
    mx, my = p.motor_xy
    ax.add_patch(Circle((mx, my), (p.motor_d + 0.6) / 2, fc="none", ec="k", lw=0.7, ls="--"))
    axx, ayy = p.rf_xy
    rrect(ax, axx, ayy, p.rf_l, p.rf_w, p.rf_r, fc="#f4f4f4", ec="k", lw=1.0)
    f = p.rf_flange
    rrect(ax, axx, ayy, p.rf_l + 2 * f, p.rf_w + 2 * f, p.rf_r + f, fc="none", ec="k", lw=0.7, ls="--")
    lmx, lmy = lid_mark_xy()
    ax.text(lmx, lmy, "OpenPocket", fontsize=7, ha="center", va="center", color="#555")
    ax.plot([-lL / 2 - 2, lL / 2 + 2], [0, 0], color="#888", lw=0.5, ls="-.")
    ax.plot([0, 0], [-lW / 2 - 2, lW / 2 + 2], color="#888", lw=0.5, ls="-.")
    hdim(ax, -lL / 2, lL / 2, lW / 2 + 6, f"{lL:.1f} -0/-0.1")
    vdim(ax, lL / 2 + 5, -lW / 2, lW / 2, f"{lW:.1f} -0/-0.1")
    hdim(ax, -bx, bx, lW / 2 + 11, f"{2 * bx:.1f}")
    vdim(ax, lL / 2 + 10, -by, by, f"{2 * by:.1f}")
    # feature coordinates table drawn as text (positions from the centre)
    g = f"7x Ø{p.mic_grille_d:.1f} THRU grille (centre + hexagon, pitch {p.mic_grille_pitch:.2f})"
    rows = [f"RF window {p.rf_l:.1f} x {p.rf_w:.1f} R{p.rf_r:.1f} THRU at ({axx:.1f}, {ayy:.1f}); underside recess {p.rf_l + 2 * f:.1f} x {p.rf_w + 2 * f:.1f} R{p.rf_r + f:.1f} ↓{p.rf_flange_t:.1f}",
            f"Mic recess 1 (underside) {p.mic_l + 0.6:.1f} x {p.mic_w + 0.6:.1f} ↓{p.mic_recess:.1f} at ({p.mic1_xy[0]:.1f}, {p.mic1_xy[1]:.1f}); {g} at ({p.mic1_xy[0] + px:.2f}, {p.mic1_xy[1] + py:.2f})",
            f"Mic recess 2 (underside) same, at ({p.mic2_xy[0]:.1f}, {p.mic2_xy[1]:.1f}); grille at ({p.mic2_xy[0] + px:.2f}, {p.mic2_xy[1] + py:.2f})",
            "No LED hole: the status LED sits under the RF window insert, which is translucent",
            f"Motor recess (underside) Ø{p.motor_d + 0.6:.1f} ↓{p.motor_recess:.1f} at ({mx:.1f}, {my:.1f})",
            f"4x Ø{p.boss_hole_d:.1f} THRU, 90° countersink Ø{p.csk_d:.1f} on the top face, mouth R{p.csk_edge_r:.1f}, at (±{bx:.1f}, ±{by:.1f})"]
    for i, r in enumerate(rows):
        ax.text(-lL / 2, -lW / 2 - 9 - i * 3.2, r, fontsize=8)
    ax.set_xlim(-lL / 2 - 14, lL / 2 + 16)
    ax.set_ylim(-lW / 2 - 30, lW / 2 + 16)

    ax2.set_title("SECTION B-B (along X through the RF window and a mic recess), scale 2:1", loc="left", fontsize=10)
    s = 2.0
    t = p.t_lid
    ax2.add_patch(Rectangle((-lL / 2 * s, 0), lL * s, t * s, fc="#e8e8e8", ec="k", lw=1.2, hatch="///"))
    # RF window through + flange recess from below
    ax2.add_patch(Rectangle(((axx - p.rf_l / 2) * s, 0), p.rf_l * s, t * s, fc="white", ec="k", lw=1.0))
    ax2.add_patch(Rectangle(((axx - p.rf_l / 2 - f) * s, 0), (p.rf_l + 2 * f) * s, p.rf_flange_t * s, fc="white", ec="k", lw=1.0))
    # mic 1 recess from below
    cx = p.mic1_xy[0]
    ax2.add_patch(Rectangle(((cx - p.mic_l / 2 - 0.3) * s, 0), (p.mic_l + 0.6) * s, p.mic_recess * s, fc="white", ec="k", lw=1.0))
    ax2.add_patch(Rectangle(((cx + px - p.mic_hole_d / 2) * s, 0), p.mic_hole_d * s, t * s, fc="white", ec="k", lw=0.8))
    vdim(ax2, (lL / 2 + 3) * s, 0, t * s, f"{t:.1f}")
    ax2.text(-lL / 2 * s, -3.5 * s, f"Plate {t:.1f} ±0.05, flatness 0.1. Recesses from the underside: RF flange ↓{p.rf_flange_t:.1f}, "
             f"mics ↓{p.mic_recess:.1f}, motor ↓{p.motor_recess:.1f} (all ±0.05). Top outer edge R{p.lid_edge_r:.1f} round.", fontsize=8.5)
    ax2.set_xlim((-lL / 2 - 8) * s, (lL / 2 + 12) * s)
    ax2.set_ylim(-6 * s, (t + 5) * s)


lid_notes = [
    "MATERIAL: Aluminium 6061-T6 plate.",
    f"OVERALL: {lL:.1f} x {lW:.1f} x {p.t_lid:.1f} mm, corners R{lR:.1f}. Outline -0/-0.1:",
    f"   the lid drops into the shell rebate ({rl:.1f} x {rw:.1f}) with 0.1 per side.",
    f"THICKNESS: {p.t_lid:.1f} ±0.05, flatness 0.1 (the lid sits flush with the shell top).",
    f"SCREW HOLES: 4x Ø{p.boss_hole_d:.1f} THRU with 90° countersink Ø{p.csk_d:.1f} on the top face,",
    f"   mouth rounded R{p.csk_edge_r:.1f} (no sharp ring). M2 flat heads seat 0.3 below the face.",
    "   Position ±0.05 (match the shell bosses).",
    f"RF WINDOW: {p.rf_l:.1f} x {p.rf_w:.1f} THRU, corners R{p.rf_r:.1f}; underside recess",
    f"   {p.rf_l + 2 * p.rf_flange:.1f} x {p.rf_w + 2 * p.rf_flange:.1f} R{p.rf_r + p.rf_flange:.1f} ↓{p.rf_flange_t:.1f} for the window insert flange.",
    f"UNDERSIDE RECESSES: 2x mic {p.mic_l + 0.6:.1f} x {p.mic_w + 0.6:.1f} ↓{p.mic_recess:.1f};",
    f"   motor Ø{p.motor_d + 0.6:.1f} ↓{p.motor_recess:.1f}. Corner R0.5 max. Depth ±0.05.",
    f"MIC GRILLES: 2x 7 holes Ø{p.mic_grille_d:.1f} THRU (acoustic), pitch {p.mic_grille_pitch:.2f}.",
    "   Deburr both sides, no chamfer.",
    f"MARKING: laser mark on the top face (STEP, ↓{p.mark_depth:.2f}), after anodizing.",
    f"EDGES: R{p.lid_edge_r:.1f} round on the top outer edge, R{p.csk_edge_r:.1f} on the countersink mouths;",
    "   break the rest 0.2 max.",
    "SURFACE: Ra 1.6 µm or better on the top face (visible product).",
    "FINISH: same as the shell, same batch: (a) bead blast + black anodize Type II;",
    "   (b) bead blast + clear anodize; (c) as machined. Quote each.",
    "QUANTITY FOR QUOTE: 1 / 10 / 100 / 1000 pcs, together with OP0-MECH-003 (shell).",
    "FILES: openpocket-lid.step (master) + this PDF. STEP governs if in conflict.",
    "ALL DIMENSIONS IN MILLIMETRES. Third-angle projection.",
]


if __name__ == "__main__":
    fig = cover_sheet()
    for ext in ("pdf", "png"):
        out = os.path.join(HERE, f"rfq-cover.{ext}")
        fig.savefig(out, dpi=150 if ext == "png" else None)
        print("wrote", out)
    plt.close(fig)
    for name, title, partno, notes, views, png in (
        ("shell", "OpenPocket v0 — SHELL (floor + walls)", "OP0-MECH-003", shell_notes, shell_views, os.path.join(RENDERS, "render-shell.png")),
        ("lid", "OpenPocket v0 — LID", "OP0-MECH-011", lid_notes, lid_views, os.path.join(RENDERS, "render-assembled.png")),
    ):
        fig = sheet(title, partno, notes, views, png)
        for ext in ("pdf", "png"):
            out = os.path.join(HERE, f"{name}-drawing.{ext}")
            fig.savefig(out, dpi=150 if ext == "png" else None)
            print("wrote", out)
        plt.close(fig)
