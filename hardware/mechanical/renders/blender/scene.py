"""OpenPocket photoreal renders (Blender 4.2 LTS, Cycles).

Run headless:
    blender -b --factory-startup -P scene.py -- --meshes <dir> --out <dir> [--shots hero,lineup] [--preview]

<dir> holds the fine meshes from openpocket_cad.py (export/render/*.stl) plus the
component meshes (export/vendor-*.stl, export/comp-*.stl). Units in the STLs are mm;
every device is an Empty scaled 0.001, so scenes are in real metres (real depth of field)
while material and face logic works in local millimetres.
"""
import argparse
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--meshes", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--shots", default="all")
ap.add_argument("--preview", action="store_true")
ap.add_argument("--samples", type=int, default=0)
args = ap.parse_args(argv)
os.makedirs(args.out, exist_ok=True)

Z0 = 3.0                       # STL frame: shell bottom at z = -3 mm; lift so the device rests on z = 0
TOP = 9.6                      # lid top face (STL frame)
LED_XY = (-31.5, 11.2)

COLORWAYS = {
    "graphite": dict(base=(0.045, 0.047, 0.052), rough=0.5, screw=(0.05, 0.05, 0.055), mark=(0.55, 0.56, 0.58)),
    "silver": dict(base=(0.78, 0.79, 0.80), rough=0.36, screw=(0.6, 0.6, 0.62), mark=(0.28, 0.29, 0.31)),
    "midnight": dict(base=(0.035, 0.07, 0.17), rough=0.40, screw=(0.05, 0.05, 0.06), mark=(0.62, 0.66, 0.74)),
    "sage": dict(base=(0.28, 0.33, 0.27), rough=0.40, screw=(0.6, 0.6, 0.62), mark=(0.86, 0.88, 0.84)),
}
ACCENT = (0.95, 0.26, 0.03)    # anodised orange button cap
LED_COLOR = (0.25, 0.85, 1.0)


# ----------------------------------------------------------------------------
# Scene helpers
# ----------------------------------------------------------------------------
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.samples = args.samples or (48 if args.preview else 384)
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.max_bounces = 12
    sc.cycles.glossy_bounces = 8
    sc.cycles.transmission_bounces = 8
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
        try:
            sc.view_settings.look = look
            break
        except TypeError:
            pass
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "8"
    return sc


def set_exposure(sc, ev):
    sc.view_settings.exposure = ev


def set_res(sc, w, h):
    k = 0.4 if args.preview else 1.0
    sc.render.resolution_x, sc.render.resolution_y = int(w * k), int(h * k)
    sc.render.resolution_percentage = 100


def mat(name, base, metal=0.0, rough=0.5, coat=0.0, bump=0.0, emit=None, emit_strength=0.0, transmission=0.0, aniso=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Anisotropic"].default_value = aniso
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    if bump:
        # bead-blast texture: fine noise on the normal
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 9.0          # object coords are mm: ~0.1 mm grain
        nz.inputs["Detail"].default_value = 6.0
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        bp.inputs["Distance"].default_value = 0.02
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def led_window_mat(on=True):
    """Smoked translucent window; the NeoPixel under it shows as a soft glow around its centre."""
    m = mat("rf-window", (0.004, 0.004, 0.005), rough=0.22)
    if not on:
        return m
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    dx = nt.nodes.new("ShaderNodeMath"); dx.operation = "SUBTRACT"; dx.inputs[1].default_value = LED_XY[0]
    dy = nt.nodes.new("ShaderNodeMath"); dy.operation = "SUBTRACT"; dy.inputs[1].default_value = LED_XY[1]
    nt.links.new(sep.outputs["X"], dx.inputs[0]); nt.links.new(sep.outputs["Y"], dy.inputs[0])
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(dx.outputs[0], cmb.inputs["X"]); nt.links.new(dy.outputs[0], cmb.inputs["Y"])
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
    nt.links.new(cmb.outputs[0], ln.inputs[0])
    rmp = nt.nodes.new("ShaderNodeMapRange")
    rmp.inputs["From Min"].default_value = 0.0
    rmp.inputs["From Max"].default_value = 5.0
    rmp.inputs["To Min"].default_value = 1.0
    rmp.inputs["To Max"].default_value = 0.0
    nt.links.new(ln.outputs["Value"], rmp.inputs["Value"])
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 2.2
    nt.links.new(rmp.outputs["Result"], pw.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 2.0
    nt.links.new(pw.outputs[0], mul.inputs[0])
    b.inputs["Emission Color"].default_value = (*LED_COLOR, 1)
    nt.links.new(mul.outputs[0], b.inputs["Emission Strength"])
    return m


def import_stl(path):
    bpy.ops.wm.stl_import(filepath=path)
    ob = bpy.context.selected_objects[0]
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(ob.data)
    bm.free()
    for poly in ob.data.polygons:
        poly.use_smooth = True
    try:
        ob.data.set_sharp_from_angle(angle=math.radians(32))
    except Exception:
        pass
    return ob


MESH_CACHE = {}


def mesh_obj(name, path, parent, material, offset=(0, 0, 0)):
    """Linked duplicate of a cached mesh, parented to a device Empty."""
    if path not in MESH_CACHE:
        src = import_stl(path)
        MESH_CACHE[path] = src.data
        bpy.data.objects.remove(src)
    me = MESH_CACHE[path]
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = parent
    ob.location = (offset[0], offset[1], offset[2] + Z0)
    if isinstance(material, list):
        if len(me.materials) == 0:
            for _m in material:
                me.materials.append(_m)
        # object-level materials so linked meshes can carry different colourways
        for i, _m in enumerate(material):
            ob.material_slots[i].link = "OBJECT"
            ob.material_slots[i].material = _m
    else:
        if len(me.materials) == 0:
            me.materials.append(material)
        ob.material_slots[0].link = "OBJECT"
        ob.material_slots[0].material = material
    return ob


def tag_bright_faces(me, kind):
    """Material slot 1 = diamond-cut bare aluminium on chamfers, the button spot face and countersink rings."""
    if me.get("tagged"):
        return
    for poly in me.polygons:
        n, c = poly.normal, poly.center
        bright = False
        if kind == "shell":
            bright |= 0.45 < n.z < 0.9 and c.z > TOP - 0.6                      # top rim chamfer
            bright |= 0.45 < n.x < 0.9 and c.x > 39.4                           # USB-C opening chamfer
            bright |= n.y > 0.95 and 23.6 < c.y < 23.8 and abs(c.x + 12) < 3.6  # button spot face
        elif kind == "lid":
            bright |= 0.3 < n.z < 0.97 and c.z > TOP - 0.7                      # lid edge round + countersink mouths
        poly.material_index = 1 if bright else 0
    me["tagged"] = True


def device(name, colorway, loc=(0, 0, 0), rot_z=0.0, explode=0.0, internals=False, led=True, flip=False):
    cw = COLORWAYS[colorway]
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    root.scale = (0.001, 0.001, 0.001)
    root.location = loc
    root.rotation_euler = (math.pi if flip else 0, 0, math.radians(rot_z))
    if flip:
        root.location = (loc[0], loc[1], loc[2] + 12.6 * 0.001)

    alu = mat(f"{name}-alu", cw["base"], metal=1.0, rough=cw["rough"], bump=0.15)
    bright = mat(f"{name}-bright", (0.92, 0.92, 0.93), metal=1.0, rough=0.08)
    screw = mat(f"{name}-screw", cw["screw"], metal=1.0, rough=0.3)
    mark = mat(f"{name}-mark", cw["mark"], metal=0.3, rough=0.7)
    cap = mat(f"{name}-cap", ACCENT, metal=1.0, rough=0.32, bump=0.1)
    win = led_window_mat(on=led)
    M = args.meshes
    e = explode

    sh = mesh_obj(f"{name}-shell", f"{M}/shell.stl", root, [alu, bright], (0, 0, -1.4 * e))
    tag_bright_faces(sh.data, "shell")
    li = mesh_obj(f"{name}-lid", f"{M}/lid.stl", root, [alu, bright], (0, 0, 2.6 * e))
    tag_bright_faces(li.data, "lid")
    mesh_obj(f"{name}-rf", f"{M}/rf-insert.stl", root, win, (0, 0, 2.6 * e))
    mesh_obj(f"{name}-marklid", f"{M}/mark-lid.stl", root, mark, (0, 0, 2.6 * e + 0.004))
    mesh_obj(f"{name}-markbot", f"{M}/mark-bottom.stl", root, mark, (0, 0, -1.4 * e - 0.004))
    mesh_obj(f"{name}-screws", f"{M}/screws.stl", root, screw, (0, 0, 4.2 * e))
    mesh_obj(f"{name}-cap", f"{M}/button-cap.stl", root, cap, (0, 1.0 * e, -1.4 * e))
    if internals or e:
        pl = mat(f"{name}-tray", (0.03, 0.03, 0.035), rough=0.55)
        pcb = mat(f"{name}-pcb", (0.02, 0.06, 0.04), rough=0.35, coat=0.6)
        blue = mat(f"{name}-pcb2", (0.02, 0.03, 0.09), rough=0.35, coat=0.6)
        pouch = mat(f"{name}-pouch", (0.75, 0.75, 0.73), metal=0.9, rough=0.35)
        mag = mat(f"{name}-mag", (0.7, 0.7, 0.72), metal=1.0, rough=0.2)
        gold = mat(f"{name}-motor", (0.6, 0.6, 0.62), metal=1.0, rough=0.25)
        amber = mat(f"{name}-kapton", (0.8, 0.45, 0.05), rough=0.3, transmission=0.3)
        white = mat(f"{name}-led", (0.9, 0.9, 0.9), rough=0.3)
        mesh_obj(f"{name}-tray", f"{M}/tray.stl", root, pl, (0, 0, -0.2 * e))
        mesh_obj(f"{name}-xiao", f"{M}/vendor-xiao.stl", root, pcb, (0, 0, 0.6 * e))
        mesh_obj(f"{name}-bat", f"{M}/comp-battery.stl", root, pouch, (0, 0, 0.3 * e))
        mesh_obj(f"{name}-sd", f"{M}/comp-sd.stl", root, blue, (0, 0, 0.6 * e))
        mesh_obj(f"{name}-sw", f"{M}/comp-switch.stl", root, pl, (0, 0, 0.0))
        mesh_obj(f"{name}-mags", f"{M}/comp-magnets.stl", root, mag, (0, 0, -1.4 * e))
        mesh_obj(f"{name}-mic1", f"{M}/vendor-mic1.stl", root, blue, (0, 0, 1.8 * e))
        mesh_obj(f"{name}-mic2", f"{M}/vendor-mic2.stl", root, blue, (0, 0, 1.8 * e))
        mesh_obj(f"{name}-ledpcb", f"{M}/comp-led.stl", root, white, (0, 0, 1.8 * e))
        mesh_obj(f"{name}-motor", f"{M}/comp-motor.stl", root, gold, (0, 0, 1.8 * e))
        mesh_obj(f"{name}-ant", f"{M}/comp-antenna.stl", root, amber, (0, 0, 1.8 * e))
    return root


def cyclorama(color=(0.5, 0.5, 0.5), rough=0.6, size=3.0, radius=0.35, back=0.6, gloss=0.0):
    """Seamless studio sweep: floor, quarter-round, back wall at +Y (cameras sit at -Y)."""
    me = bpy.data.meshes.new("cyc")
    bm = bmesh.new()
    pts = [(-size, 0.0), (back - radius, 0.0)]
    for i in range(1, 16):
        a = math.radians(90 * i / 16)
        pts.append((back - radius + radius * math.sin(a), radius - radius * math.cos(a)))
    pts += [(back, radius), (back, 2.5)]
    rows = []
    for (u, z) in pts:
        rows.append([bm.verts.new((x, u, z)) for x in (-size, size)])
    for a, b in zip(rows, rows[1:]):
        bm.faces.new((a[0], a[1], b[1], b[0]))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("cyc", me)
    bpy.context.scene.collection.objects.link(ob)
    for poly in me.polygons:
        poly.use_smooth = True
    m = mat("cyc", color, rough=rough, coat=gloss)
    me.materials.append(m)
    return ob


def area(name, loc, target, size, power, color=(1, 1, 1), shape="RECTANGLE", size_y=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = shape
    ld.size = size
    if size_y:
        ld.size_y = size_y
    ld.energy = power
    ld.color = color
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    return ob


def look_at(ob, target):
    d = Vector(target) - Vector(ob.location)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, lens=85, fstop=0.0, focus=None):
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.clip_start = 0.005
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = focus if focus else (Vector(target) - Vector(loc)).length
    ob = bpy.data.objects.new("cam", cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    bpy.context.scene.camera = ob
    return ob


def world(color=(0.02, 0.02, 0.025), strength=1.0):
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*color, 1)
    bg.inputs["Strength"].default_value = strength
    bpy.context.scene.world = w


def render(sc, name):
    sc.render.filepath = os.path.join(args.out, name + (".preview" if args.preview else "") + ".png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath, flush=True)


def orbit(target, dist, elev, azim):
    """Camera position at distance / elevation / azimuth (deg) around target."""
    e, a = math.radians(elev), math.radians(azim)
    t = Vector(target)
    return (t.x + dist * math.cos(e) * math.cos(a), t.y + dist * math.cos(e) * math.sin(a), t.z + dist * math.sin(e))


# ----------------------------------------------------------------------------
# Shots
# ----------------------------------------------------------------------------
def shot_hero():
    """Graphite unit, dark studio, rim lights tracing the diamond-cut edges, LED on."""
    sc = reset(); set_res(sc, 3000, 2000); set_exposure(sc, -2.6)
    world((0.004, 0.004, 0.005), 1.0)
    cyclorama((0.012, 0.012, 0.014), rough=0.35, gloss=0.3)
    device("hero", "graphite", rot_z=-28)
    tgt = (0.0, 0.004, 0.008)
    camera(orbit(tgt, 0.31, 22, -62), tgt, lens=90, fstop=16, focus=0.31)
    area("key", orbit(tgt, 0.35, 55, -120), tgt, 0.35, 28, (1.0, 0.97, 0.93))
    area("rim", orbit(tgt, 0.30, 12, 75), tgt, 0.6, 22, (0.85, 0.9, 1.0), size_y=0.05)
    area("rim2", orbit(tgt, 0.30, 18, 165), tgt, 0.5, 10, (1.0, 0.95, 0.9), size_y=0.04)
    area("top", (0, 0, 0.5), tgt, 0.4, 6)
    render(sc, "openpocket-hero")


def shot_lineup():
    """Four colourways side by side on a light sweep."""
    sc = reset(); set_res(sc, 3200, 1800); set_exposure(sc, -1.8)
    world((0.8, 0.8, 0.8), 0.25)
    cyclorama((0.62, 0.62, 0.6), rough=0.7, back=0.35)
    order = ["silver", "graphite", "midnight", "sage"]
    for i, cw in enumerate(order):
        x = (i - 1.5) * 0.058
        device(f"u-{cw}", cw, loc=(x, 0.012 * (i % 2), 0), rot_z=90 + 8 * (i - 1.5))
    tgt = (0.0, 0.0, 0.0)
    camera(orbit(tgt, 0.50, 30, -90), tgt, lens=70, fstop=16)
    area("key", orbit(tgt, 0.6, 60, -130), tgt, 0.8, 70)
    area("fill", orbit(tgt, 0.6, 30, -30), tgt, 0.8, 25)
    area("rim", orbit(tgt, 0.5, 20, 90), tgt, 1.0, 30, size_y=0.12)
    render(sc, "openpocket-colorways")


def shot_exploded():
    """Exploded stack: shell, tray and electronics, lid, screws."""
    sc = reset(); set_res(sc, 2400, 3000); set_exposure(sc, -1.8)
    world((0.85, 0.85, 0.86), 0.3)
    cyclorama((0.7, 0.7, 0.71), rough=0.8, back=0.5)
    device("ex", "graphite", loc=(0, 0, 0.0135), rot_z=-30, explode=9.0)
    tgt = (0.0, 0.0, 0.022)
    camera(orbit(tgt, 0.34, 30, -60), tgt, lens=75, fstop=16)
    area("key", orbit(tgt, 0.5, 55, -120), tgt, 0.7, 45)
    area("fill", orbit(tgt, 0.5, 20, -10), tgt, 0.7, 18)
    area("rim", orbit(tgt, 0.45, 25, 110), tgt, 0.8, 30, size_y=0.1)
    render(sc, "openpocket-exploded")


def shot_detail():
    """Macro on the USB-C end and the orange button, shallow focus."""
    sc = reset(); set_res(sc, 3000, 2000); set_exposure(sc, -2.8)
    world((0.01, 0.01, 0.012), 1.0)
    cyclorama((0.02, 0.02, 0.022), rough=0.4, gloss=0.2)
    device("det", "silver", rot_z=0)
    tgt = (0.02, 0.008, 0.006)
    camera(orbit(tgt, 0.26, 16, 40), tgt, lens=100, fstop=11, focus=0.25)
    area("key", orbit(tgt, 0.25, 45, 80), tgt, 0.25, 9, (1.0, 0.96, 0.92))
    area("rim", orbit(tgt, 0.2, 10, -10), tgt, 0.3, 6, (0.85, 0.9, 1.0), size_y=0.03)
    area("back", orbit(tgt, 0.25, 30, 170), tgt, 0.3, 5)
    area("soft", (0.02, -0.05, 0.3), tgt, 0.5, 8)
    render(sc, "openpocket-detail")


def shot_top():
    """Flat lay from above, midnight unit, soft window light."""
    sc = reset(); set_res(sc, 2400, 2400); set_exposure(sc, -1.6)
    world((0.9, 0.9, 0.9), 0.2)
    cyclorama((0.72, 0.70, 0.66), rough=0.85, size=1.0)
    device("top", "midnight", rot_z=-18)
    tgt = (0.0, 0.0, 0.0)
    camera((0.0, -0.015, 0.30), tgt, lens=85)
    area("win", (-0.35, -0.25, 0.45), tgt, 0.6, 120, (1.0, 0.97, 0.92))
    area("fill", (0.4, 0.3, 0.4), tgt, 0.8, 20)
    render(sc, "openpocket-top")


def shot_bottom():
    """Upside down: bottom engraving, magnets hidden under 0.9 mm of aluminium."""
    sc = reset(); set_res(sc, 3000, 2000); set_exposure(sc, -2.0)
    world((0.004, 0.004, 0.005), 1.0)
    cyclorama((0.014, 0.014, 0.016), rough=0.35, gloss=0.3)
    device("bot", "graphite", rot_z=-15, flip=True)
    tgt = (0.0, 0.0, 0.006)
    camera(orbit(tgt, 0.34, 40, -70), tgt, lens=90, fstop=16)
    area("key", orbit(tgt, 0.35, 60, -140), tgt, 0.35, 24, (1.0, 0.97, 0.93))
    area("rim", orbit(tgt, 0.3, 14, 80), tgt, 0.6, 20, (0.85, 0.9, 1.0), size_y=0.05)
    area("rim2", orbit(tgt, 0.3, 20, 170), tgt, 0.5, 8, size_y=0.04)
    render(sc, "openpocket-bottom")


SHOTS = {"hero": shot_hero, "lineup": shot_lineup, "exploded": shot_exploded,
         "detail": shot_detail, "top": shot_top, "bottom": shot_bottom}
todo = list(SHOTS) if args.shots == "all" else args.shots.split(",")
for s in todo:
    MESH_CACHE.clear()
    SHOTS[s]()
