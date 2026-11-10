# Blender 4.0 headless scene: 3D Pip & Pebble in a sunny meadow, lip-synced from lipsync.json.
# usage: blender -b --python scene_blender.py -- <workdir> [frame_or_all] [samples]
import bpy, sys, json, math, random
argv = sys.argv[sys.argv.index("--") + 1:]
WD = argv[0]; WHICH = argv[1] if len(argv) > 1 else "all"; SAMPLES = int(argv[2]) if len(argv) > 2 else 20
LS = json.load(open(f"{WD}/lipsync.json")); FPS = LS["fps"]; NF = int(LS["T"]["end"] * FPS)
random.seed(4)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = False
ENGINE = argv[3] if len(argv) > 3 else "CYCLES"
if ENGINE == "EEVEE":
    sc.render.engine = "BLENDER_EEVEE"; ee = sc.eevee
    for k, v in (("taa_render_samples", 12), ("use_soft_shadows", True), ("use_gtao", True), ("gtao_distance", 1.5), ("use_bloom", True), ("bloom_intensity", 0.02), ("shadow_cube_size", "2048"), ("shadow_cascade_size", "2048"), ("use_ssr", False)):
        try: setattr(ee, k, v)
        except Exception as e: print("eevee opt", k, e)
sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 1; sc.cycles.transparent_max_bounces = 2
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1280, 720, 100
sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
sc.render.image_settings.file_format = "PNG"; sc.render.filepath = f"{WD}/bl/f"
try:
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"
except Exception: pass
sc.render.film_transparent = False

def mat(name, rgb, rough=0.6, sss=0.0, spec=0.3, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    for k, v in (("Subsurface Weight", sss), ("Subsurface", sss)):
        if k in p.inputs: p.inputs[k].default_value = v; break
    if "Specular IOR Level" in p.inputs: p.inputs["Specular IOR Level"].default_value = spec
    if emit and "Emission Strength" in p.inputs: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = emit
    return m
def srgb(h): h = h.lstrip("#"); return tuple(((int(h[i:i+2], 16) / 255) ** 2.2) for i in (0, 2, 4))
def sphere(name, loc, scale, m, parent=None, seg=40):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=1, location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = scale; bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None); sc.collection.objects.link(o); o.location = loc
    if parent: o.parent = parent
    return o

# ---------- world, light, ground ----------
w = bpy.data.worlds.new("Sky"); sc.world = w; w.use_nodes = True
nt = w.node_tree; bg = nt.nodes["Background"]
grad = nt.nodes.new("ShaderNodeTexGradient"); grad.gradient_type = "LINEAR"
coord = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, -math.pi / 2, 0)
ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color = (*srgb("#dff3ff"), 1); ramp.color_ramp.elements[1].color = (*srgb("#5fb6ef"), 1)
nt.links.new(coord.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], grad.inputs["Vector"])
nt.links.new(grad.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 1.0
bpy.ops.object.light_add(type="SUN", location=(5, -5, 10)); sun = bpy.context.active_object
sun.data.energy = 4.0; sun.data.angle = math.radians(8); sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35)); sun.data.color = (1, 0.95, 0.85)
bpy.ops.object.light_add(type="AREA", location=(-6, -4, 5)); fill = bpy.context.active_object
fill.data.energy = 400; fill.data.size = 6; fill.data.color = (0.8, 0.9, 1); fill.rotation_euler = (math.radians(60), 0, math.radians(-55))
gm = mat("Grass", srgb("#72c64e"), 0.95)
n = gm.node_tree.nodes; noise = n.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 3
cr = n.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (*srgb("#5fb23f"), 1); cr.color_ramp.elements[1].color = (*srgb("#8ad85f"), 1)
gm.node_tree.links.new(noise.outputs["Fac"], cr.inputs["Fac"]); gm.node_tree.links.new(cr.outputs["Color"], n["Principled BSDF"].inputs["Base Color"])
sphere("Ground", (0, 0, -60), (60, 60, 60), gm, seg=128)
hills = mat("Hills", srgb("#9ad879"), 1.0)
for i, (x, y, r) in enumerate([(-14, 28, 12), (6, 34, 15), (24, 26, 11), (-30, 22, 10)]): sphere(f"Hill{i}", (x, y, -r * 0.55), (r * 1.4, r, r), hills, seg=48)
trunk, leaf, apple = mat("Trunk", srgb("#8a5a3b"), 0.9), mat("Leaf", srgb("#46a84a"), 0.8, 0.1), mat("Apple", srgb("#e8473f"), 0.4, spec=0.6)
for i, (x, y, s) in enumerate([(-4.2, 5.5, 1.2), (4.6, 7.5, 1.4), (-8, 10, 1.6), (9, 12, 1.5)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16 * s, depth=2.2 * s, location=(x, y, 1.1 * s)); t = bpy.context.active_object; bpy.ops.object.shade_smooth(); t.data.materials.append(trunk)
    for j in range(3): sphere(f"Leaf{i}{j}", (x + (j - 1) * 0.55 * s, y + random.uniform(-.2, .2), 2.6 * s + (j == 1) * 0.5 * s), (0.95 * s,) * 3, leaf, seg=32)
    for j in range(4): sphere(f"Apple{i}{j}", (x + random.uniform(-.8, .8) * s, y - 0.8 * s, 2.5 * s + random.uniform(-.3, .5) * s), (0.12 * s,) * 3, apple, seg=16)
petal = [mat(f"P{i}", srgb(c), 0.6) for i, c in enumerate(["#ff6fa8", "#ffd23f", "#ffffff", "#b07cff"])]; center = mat("Ctr", srgb("#ff9f1c"))
for i in range(70):
    x, y = random.uniform(-7, 7), random.uniform(-2.5, 6)
    if abs(x) < 1.6 and -1 < y < 1.5: continue
    sphere(f"Fl{i}", (x, y, 0.04), (0.09, 0.09, 0.03), petal[i % 4], seg=12); sphere(f"Fc{i}", (x, y, 0.06), (0.04, 0.04, 0.02), center, seg=8)

# ---------- Pip (bunny) ----------
fur, belly, pink, eye, white = mat("Fur", srgb("#f7e6d4"), 0.85, 0.15), mat("Belly", srgb("#fffaf2"), 0.9, 0.1), mat("Pink", srgb("#ffb3c6"), 0.8), mat("Eye", srgb("#120a06"), 0.08, spec=0.9), mat("White", (1, 1, 1), 0.2, emit=0.6)
blush, scarf, mouthm = mat("Blush", srgb("#ff8fa8"), 0.9), mat("Scarf", srgb("#3d8bff"), 0.7), mat("Mouth", srgb("#5a1824"), 0.6)
PIP = empty("Pip", (-1.3, 0, 0)); PIP.rotation_euler = (0, 0, math.radians(28))
sphere("PBody", (0, 0, 0.75), (0.62, 0.55, 0.7), fur, PIP); sphere("PBelly", (0, -0.36, 0.72), (0.38, 0.22, 0.45), belly, PIP)
PH = empty("PHead", (0, 0, 1.55), PIP)
sphere("PHeadM", (0, 0, 0.2), (0.62, 0.56, 0.56), fur, PH)
EARS = []
for s in (-1, 1):
    ep = empty(f"PEar{s}", (s * 0.24, 0.05, 0.62), PH); EARS.append(ep)
    sphere("ear", (0, 0, 0.5), (0.17, 0.11, 0.55), fur, ep); sphere("earin", (0, -0.06, 0.5), (0.09, 0.06, 0.42), pink, ep)
    sphere("eye", (s * 0.21, -0.48, 0.28), (0.1, 0.07, 0.13), eye, PH); sphere("hl", (s * 0.21 - 0.03, -0.55, 0.34), (0.03, 0.02, 0.03), white, PH)
    sphere("blush", (s * 0.38, -0.42, 0.12), (0.09, 0.03, 0.055), blush, PH)
sphere("nose", (0, -0.55, 0.16), (0.06, 0.04, 0.045), pink, PH)
PM = sphere("PMouth", (0, -0.52, 0.03), (0.07, 0.03, 0.02), mouthm, PH)
bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.09, location=(0, 0, 1.3)); sf = bpy.context.active_object; bpy.ops.object.shade_smooth(); sf.data.materials.append(scarf); sf.parent = PIP
for s in (-1, 1):
    sphere("foot", (s * 0.3, -0.18, 0.08), (0.2, 0.3, 0.1), fur, PIP); sphere("arm", (s * 0.52, -0.2, 0.85), (0.13, 0.13, 0.2), fur, PIP)
sphere("tail", (0, 0.55, 0.6), (0.2, 0.2, 0.2), belly, PIP)

# ---------- Pebble (turtle) ----------
shell, shell2, skin, rimm = mat("Shell", srgb("#4fae47"), 0.5, spec=0.5), mat("Shell2", srgb("#8fdc7a"), 0.55), mat("Skin", srgb("#a8e08a"), 0.8, 0.12), mat("Rim", srgb("#e6d27a"), 0.6)
PEB = empty("Pebble", (1.6, 0.3, 0)); PEB.rotation_euler = (0, 0, math.radians(-62))
sphere("PShell", (0, 0, 0.45), (0.95, 0.8, 0.62), shell, PEB)
for i, (x, y, z) in enumerate([(0, 0, 1.05), (0.45, -0.25, 0.85), (-0.45, -0.25, 0.85), (0.45, 0.3, 0.85), (-0.45, 0.3, 0.85), (0, -0.55, 0.75)]): sphere(f"hex{i}", (x, y, z), (0.24, 0.24, 0.07), shell2, PEB, seg=6)
bpy.ops.mesh.primitive_torus_add(major_radius=0.86, minor_radius=0.07, location=(0, 0, 0.32)); r = bpy.context.active_object; r.scale = (1, 0.86, 1); bpy.ops.object.shade_smooth(); r.data.materials.append(rimm); r.parent = PEB
LEGS = []
for i, (x, y) in enumerate([(0.55, -0.5), (-0.55, -0.5), (0.55, 0.5), (-0.55, 0.5)]): LEGS.append(sphere(f"leg{i}", (x, y, 0.13), (0.2, 0.2, 0.15), skin, PEB))
BH = empty("PebHead", (0, -1.0, 0.55), PEB)
sphere("neck", (0, 0.25, -0.05), (0.2, 0.25, 0.2), skin, BH); sphere("bhead", (0, 0, 0.1), (0.38, 0.36, 0.34), skin, BH)
for s in (-1, 1):
    sphere("beye", (s * 0.15, -0.3, 0.2), (0.08, 0.06, 0.1), eye, BH); sphere("bhl", (s * 0.15 - 0.025, -0.36, 0.25), (0.025, 0.02, 0.025), white, BH)
    sphere("bblush", (s * 0.25, -0.25, 0.02), (0.07, 0.03, 0.045), blush, BH)
BM = sphere("BMouth", (0, -0.34, -0.06), (0.06, 0.025, 0.015), mouthm, BH)

# ---------- ball ----------
ballm = mat("Ball", srgb("#e8262e"), 0.3, spec=0.7)
BALL = sphere("Ball", (-0.6, -0.55, 0.22), (0.22, 0.22, 0.22), ballm, seg=32)

# ---------- camera ----------
bpy.ops.object.camera_add(location=(0, -9.5, 2.6)); cam = bpy.context.active_object; sc.camera = cam
cam.data.lens = 36; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.2
tgt = empty("CamTarget", (0.1, 0, 1.25)); cam.data.dof.focus_object = tgt
con = cam.constraints.new("TRACK_TO"); con.target = tgt; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"

# ---------- animation ----------
mp, mb = LS["mouth"]["PIP"], LS["mouth"]["PEB"]
t_peb = LS["T"]["PEB"]
for f in range(1, NF + 1):
    t = (f - 1) / FPS; sc.frame_set(f)
    hop = abs(math.sin(t * 4.2)) * 0.18 if t < LS["T"]["PIP"][1] + 0.3 else abs(math.sin(t * 5)) * 0.08
    PIP.location.z = hop; PIP.keyframe_insert("location", index=2)
    PH.rotation_euler = (math.sin(t * 2.1) * 0.06, math.sin(t * 1.3) * 0.08, math.sin(t * 1.7) * 0.1); PH.keyframe_insert("rotation_euler")
    for k, ep in enumerate(EARS):
        ep.rotation_euler = (0, (1 if k else -1) * (0.18 + math.sin(t * 5 + k) * 0.08), 0); ep.keyframe_insert("rotation_euler")
    i = min(f - 1, len(mp) - 1)
    PM.scale = (0.07 + mp[i] * 0.03, 0.03, 0.02 + mp[i] * 0.09); PM.keyframe_insert("scale")
    BM.scale = (0.06 + mb[i] * 0.03, 0.025, 0.015 + mb[i] * 0.08); BM.keyframe_insert("scale")
    walk = min(1, t / 2.6)  # Pebble walks in
    PEB.location = (1.6 + (1 - walk) * 2.4, 0.3, abs(math.sin(t * 6)) * 0.03 * (walk < 1)); PEB.keyframe_insert("location")
    for k, lg in enumerate(LEGS):
        lg.location.z = 0.13 + (max(0, math.sin(t * 9 + k * math.pi)) * 0.08 if walk < 1 else 0); lg.keyframe_insert("location", index=2)
    BH.rotation_euler = (math.sin(t * 1.5) * 0.05 + (0.15 if t > t_peb[0] else 0), 0, math.sin(t * 1.1) * 0.08); BH.keyframe_insert("rotation_euler")
    roll = min(1, max(0, (t - (t_peb[1] - 0.2)) / 1.2)); e = roll * roll * (3 - 2 * roll)   # Pip rolls the ball to Pebble
    BALL.location = (-0.55 + e * 1.35, -0.6 - e * 0.25, 0.22); BALL.rotation_euler = (e * 8, 0, 0); BALL.keyframe_insert("location"); BALL.keyframe_insert("rotation_euler")
    push = min(1, t / LS["T"]["end"]); cam.location = (0.25 * math.sin(t * .6), -9.5 + push * 1.8, 2.6 - push * 0.25); cam.keyframe_insert("location")

if WHICH == "all":
    bpy.ops.render.render(animation=True)
else:
    sc.frame_set(int(WHICH)); sc.render.filepath = f"{WD}/test_{WHICH}.png"; bpy.ops.render.render(write_still=True)
