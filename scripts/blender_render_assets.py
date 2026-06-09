from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp" / "blender-renders"
VARIANT = "production"

STYLES = {
    "production": {
        "metal": (0.2, 0.225, 0.265, 1),
        "dark": (0.03, 0.036, 0.05, 1),
        "trim": (0.12, 0.145, 0.155, 1),
        "rust": (0.7, 0.38, 0.13, 1),
        "light": 720,
        "ortho": 3.85,
        "greeble": 1.35,
    },
    "a-industrial": {
        "metal": (0.2, 0.22, 0.25, 1),
        "dark": (0.035, 0.04, 0.05, 1),
        "trim": (0.16, 0.14, 0.11, 1),
        "rust": (0.8, 0.42, 0.12, 1),
        "light": 560,
        "ortho": 4.05,
        "greeble": 1.25,
    },
    "b-arcology": {
        "metal": (0.28, 0.31, 0.36, 1),
        "dark": (0.05, 0.06, 0.08, 1),
        "trim": (0.08, 0.1, 0.14, 1),
        "rust": (0.45, 0.47, 0.5, 1),
        "light": 760,
        "ortho": 3.9,
        "greeble": 0.85,
    },
    "c-hero-industrial": {
        "metal": (0.18, 0.2, 0.23, 1),
        "dark": (0.025, 0.03, 0.04, 1),
        "trim": (0.13, 0.15, 0.15, 1),
        "rust": (0.72, 0.38, 0.12, 1),
        "light": 660,
        "ortho": 3.85,
        "greeble": 1.55,
    },
    "d-hero-neon": {
        "metal": (0.24, 0.27, 0.32, 1),
        "dark": (0.035, 0.045, 0.065, 1),
        "trim": (0.08, 0.1, 0.13, 1),
        "rust": (0.38, 0.42, 0.48, 1),
        "light": 860,
        "ortho": 3.8,
        "greeble": 1.15,
    },
}

ASSETS = {
    "interstellar-lab": {"color": (0.2, 0.9, 1.0, 1), "accent": (0.9, 1.0, 1.0, 1), "kind": "lab"},
    "quantum-replicator": {"color": (0.75, 0.25, 1.0, 1), "accent": (0.4, 0.95, 1.0, 1), "kind": "replicator"},
    "interstellar-dust-collector": {"color": (1.0, 0.72, 0.14, 1), "accent": (1.0, 1.0, 0.72, 1), "kind": "collector"},
    "stellar-fusion-drive": {"color": (0.18, 0.75, 1.0, 1), "accent": (0.9, 1.0, 1.0, 1), "kind": "drive"},
    "antimatter-drive": {"color": (0.78, 0.22, 1.0, 1), "accent": (1.0, 0.86, 1.0, 1), "kind": "drive"},
    "interstellar-foundry": {"color": (1.0, 0.38, 0.1, 1), "accent": (1.0, 0.8, 0.35, 1), "kind": "foundry"},
    "interstellar-electromagnetic-plant": {"color": (0.72, 0.22, 1.0, 1), "accent": (0.35, 0.95, 1.0, 1), "kind": "electromagnetic"},
    "interstellar-biochamber": {"color": (0.2, 0.95, 0.35, 1), "accent": (0.86, 1.0, 0.55, 1), "kind": "biochamber"},
    "interstellar-cryogenic-plant": {"color": (0.35, 0.85, 1.0, 1), "accent": (0.92, 1.0, 1.0, 1), "kind": "cryogenic"},
}


def material(name: str, color, emission: float = 0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.62
    bsdf.inputs["Metallic"].default_value = 0.35
    bsdf.inputs["Alpha"].default_value = color[3]
    bsdf.inputs["Emission Color"].default_value = color
    bsdf.inputs["Emission Strength"].default_value = emission
    mat.diffuse_color = color
    return mat


def add_cube(name, location, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("soft bevel", "BEVEL")
    bevel.width = 0.05
    bevel.segments = 3
    obj.modifiers.new("weighted normals", "WEIGHTED_NORMAL")
    return obj


def add_panel(name, location, scale, mat):
    obj = add_cube(name, location, scale, mat)
    obj.modifiers["soft bevel"].width = 0.018
    return obj


def add_cylinder(name, location, radius, depth, mat, vertices=48, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("rim bevel", "BEVEL")
    bevel.width = 0.025
    bevel.segments = 2
    obj.modifiers.new("weighted normals", "WEIGHTED_NORMAL")
    return obj


def add_uv_sphere(name, location, radius, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def add_torus(name, location, major_radius, minor_radius, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(
        major_segments=72,
        minor_segments=12,
        major_radius=major_radius,
        minor_radius=minor_radius,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj.modifiers.new("weighted normals", "WEIGHTED_NORMAL")
    return obj


def add_bolt_ring(mat, z=0.34, radius=0.94, count=8):
    for i in range(count):
        angle = i * math.tau / count
        add_uv_sphere("bolt", (math.cos(angle) * radius, math.sin(angle) * radius, z), 0.035, mat)


def add_machine_greebles(primary, accent, dark, trim, rust):
    style = STYLES[VARIANT]
    density = style["greeble"]
    add_bolt_ring(trim, count=8 if density <= 1 else 12)
    add_panel("top_access_hatch", (-0.42, 0.35, 1.08), (0.42, 0.34, 0.04), trim)
    add_panel("rear_access_hatch", (0.44, 0.36, 1.08), (0.38, 0.32, 0.04), dark)
    add_panel("front_trim_l", (-0.68, -0.86, 0.73), (0.12, 0.08, 0.58), trim)
    add_panel("front_trim_r", (0.68, -0.86, 0.73), (0.12, 0.08, 0.58), trim)
    for x in (-0.62, -0.38, -0.14, 0.14, 0.38, 0.62):
        add_panel("vent_slat", (x, -0.88, 0.48), (0.12, 0.045, 0.055), dark)
    for x in (-0.92, 0.92):
        add_cylinder("side_conduit", (x, 0.02, 0.82), 0.045, 1.2, rust, vertices=16, rotation=(math.pi / 2, 0, 0))
        add_uv_sphere("signal_light", (x * 0.92, -0.72, 0.98), 0.055, accent)
    if density > 1:
        for y in (-0.38, 0.0, 0.38):
            add_panel("side_rib_l", (-0.96, y, 0.54), (0.08, 0.08, 0.4), trim)
            add_panel("side_rib_r", (0.96, y, 0.54), (0.08, 0.08, 0.4), trim)
    add_panel("energy_status", (0, -0.895, 1.02), (0.42, 0.05, 0.08), accent)


def setup_scene():
    style = STYLES[VARIANT]
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 32
    scene.render.resolution_x = 256
    scene.render.resolution_y = 256
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.camera = None

    bpy.ops.object.light_add(type="AREA", location=(-3.8, -4.2, 6.0))
    key = bpy.context.object
    key.name = "key_light"
    key.data.energy = style["light"]
    key.data.size = 4
    bpy.ops.object.light_add(type="POINT", location=(3.0, 2.5, 3.0))
    fill = bpy.context.object
    fill.name = "accent_fill"
    fill.data.energy = 80

    bpy.ops.object.camera_add(location=(4.8, -6.2, 5.2), rotation=(math.radians(60), 0, math.radians(41)))
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = style["ortho"]
    scene.camera = camera


def build_asset(name: str, frame: int):
    spec = ASSETS[name]
    style = STYLES[VARIANT]
    primary = material("primary", spec["color"], 0.22 if VARIANT != "a-industrial" else 0.12)
    accent = material("accent", spec["accent"], 1.8 if VARIANT != "a-industrial" else 1.25)
    dark = material("dark_metal", style["dark"], 0)
    metal = material("machine_metal", style["metal"], 0)
    trim = material("trim_metal", style["trim"], 0)
    rust = material("warm_wear", style["rust"], 0)

    add_cylinder("base", (0, 0, 0.15), 1.05, 0.3, dark)
    add_cube("body", (0, 0, 0.65), (1.8, 1.45, 0.8), metal)
    add_cube("front_panel", (0, -0.78, 0.72), (1.2, 0.12, 0.5), primary)
    add_machine_greebles(primary, accent, dark, trim, rust)

    kind = spec["kind"]
    angle = frame * math.tau / 4

    if kind in {"lab", "replicator"}:
        add_torus("energy_ring", (0, -0.15, 1.26), 0.48, 0.035, primary, rotation=(0.35, 0.15, angle))
        add_uv_sphere("core", (0, -0.15, 1.25), 0.42, accent)
        add_cylinder("core_socket", (0, -0.15, 1.08), 0.5, 0.12, trim)
        for i in range(6):
            a = angle + i * math.tau / 6
            add_cylinder("core_arm", (math.cos(a) * 0.55, math.sin(a) * 0.55, 1.18), 0.04, 0.58, primary, vertices=16, rotation=(math.pi / 2, 0, a))
        if kind == "replicator":
            add_torus("matter_ring", (0, -0.15, 1.42), 0.32, 0.025, accent, rotation=(math.pi / 2, 0, -angle))
            for i in range(3):
                a = angle * 0.5 + i * math.tau / 3
                add_uv_sphere("replication_particle", (math.cos(a) * 0.36, math.sin(a) * 0.36 - 0.15, 1.58), 0.055, accent)
        else:
            add_panel("lab_screen", (0, -0.92, 1.2), (0.64, 0.05, 0.18), accent)
            for x in (-0.34, 0.34):
                add_cylinder("lab_antenna", (x, 0.42, 1.4), 0.025, 0.56, trim)
                add_uv_sphere("lab_beacon", (x, 0.42, 1.72), 0.075, accent)
    elif kind == "collector":
        add_cylinder("collector_mast", (0, -0.05, 1.24), 0.075, 0.78, trim)
        add_torus("collector_field", (0, -0.05, 1.42), 0.5, 0.018, accent, rotation=(0.2, 0.7, angle))
        for i in range(4):
            a = angle + i * math.tau / 4
            add_cylinder("collector_arm", (math.cos(a) * 0.62, math.sin(a) * 0.62, 1.08), 0.055, 1.2, primary, vertices=16, rotation=(math.pi / 2, 0, a))
            add_uv_sphere("collector_node", (math.cos(a) * 1.18, math.sin(a) * 1.18, 1.08), 0.15, accent)
        add_uv_sphere("dust_orbit", (math.cos(angle + 0.7) * 0.42, math.sin(angle + 0.7) * 0.42, 1.48), 0.08, accent)
        add_uv_sphere("dust_pulse", (-0.22, -0.08, 1.42 + 0.08 * math.sin(angle)), 0.06 + 0.02 * frame, primary)
    elif kind == "drive":
        add_cube("engine_nozzle", (0, -0.9, 0.62), (0.9, 0.45, 0.5), dark)
        add_cylinder("thruster_glow", (0, -1.18, 0.62), 0.26 + frame * 0.02, 0.16, accent, rotation=(math.pi / 2, 0, 0))
        add_cube("wing_l", (-0.78, 0.05, 0.72), (0.5, 1.25, 0.18), primary)
        add_cube("wing_r", (0.78, 0.05, 0.72), (0.5, 1.25, 0.18), primary)
        add_cylinder("fuel_line_l", (-0.42, -0.06, 1.04), 0.04, 0.86, trim, vertices=16, rotation=(math.pi / 2, 0, 0))
        add_cylinder("fuel_line_r", (0.42, -0.06, 1.04), 0.04, 0.86, trim, vertices=16, rotation=(math.pi / 2, 0, 0))
        for x in (-0.48, 0, 0.48):
            add_cylinder("exhaust_ring", (x, -1.07, 0.62), 0.11, 0.1, rust, vertices=24, rotation=(math.pi / 2, 0, 0))
        add_torus("drive_containment", (0, -0.02, 1.06), 0.42, 0.035, accent, rotation=(0.1, 0.7, angle))
    elif kind == "foundry":
        add_cylinder("furnace", (0, -0.1, 1.2), 0.48, 0.55, primary)
        add_uv_sphere("molten_core", (0, -0.1, 1.3), 0.28 + 0.03 * math.sin(angle), accent)
        add_cylinder("chimney_l", (-0.54, 0.28, 1.28), 0.12, 0.62, dark)
        add_cylinder("chimney_r", (0.54, 0.28, 1.18), 0.1, 0.48, dark)
        add_torus("molten_lip", (0, -0.1, 1.46), 0.42, 0.035, rust)
    elif kind == "electromagnetic":
        for x in (-0.45, 0, 0.45):
            add_cylinder("coil", (x, -0.08, 1.2), 0.22, 0.5, primary, rotation=(math.pi / 2, 0, 0))
            add_cylinder("coil_core", (x, -0.08, 1.2), 0.1, 0.58, trim, vertices=24, rotation=(math.pi / 2, 0, 0))
        add_cylinder("arc", (0, -0.08, 1.2), 0.08, 1.25, accent, rotation=(0, math.pi / 2, angle))
        for x in (-0.72, 0.72):
            add_cylinder("tesla_post", (x, 0.28, 1.22), 0.045, 0.58, trim)
            add_uv_sphere("tesla_cap", (x, 0.28, 1.54), 0.09, accent)
    elif kind == "biochamber":
        add_torus("bio_tank_rim", (0, -0.05, 1.22), 0.44, 0.035, trim)
        add_uv_sphere("bio_core", (0, -0.05, 1.22), 0.42, primary)
        add_uv_sphere("bio_pulse", (0.2 * math.cos(angle), -0.05 + 0.2 * math.sin(angle), 1.34), 0.12 + 0.04 * frame, accent)
        add_uv_sphere("bio_bubble", (-0.26, -0.12, 1.18 + 0.06 * math.sin(angle)), 0.08 + 0.02 * (3 - frame), accent)
    elif kind == "cryogenic":
        add_cylinder("cryo_tank_l", (-0.42, -0.05, 1.16), 0.22, 0.72, primary)
        add_cylinder("cryo_tank_r", (0.42, -0.05, 1.16), 0.22, 0.72, primary)
        add_uv_sphere("frost_core", (0, -0.08, 1.26), 0.26, accent)
        add_uv_sphere("cold_vapor", (0.2 * math.cos(angle), -0.25 + 0.12 * math.sin(angle), 1.55), 0.11, accent)
        add_cylinder("cryo_pipe", (0, 0.28, 1.1), 0.05, 1.1, trim, vertices=16, rotation=(math.pi / 2, 0, math.pi / 2))
        add_torus("frost_ring", (0, -0.08, 1.28), 0.32, 0.025, accent, rotation=(math.pi / 2, 0, angle))

    empty = bpy.data.objects.new("rotator", None)
    bpy.context.collection.objects.link(empty)
    for obj in bpy.context.scene.objects:
        if obj.type in {"MESH"}:
            obj.parent = empty
    empty.rotation_euler[2] = math.radians(45)


def render_asset(name: str):
    asset_dir = OUT / name
    asset_dir.mkdir(parents=True, exist_ok=True)
    for frame in range(4):
        setup_scene()
        build_asset(name, frame)
        bpy.context.scene.frame_set(frame + 1)
        bpy.context.scene.render.filepath = str(asset_dir / f"frame_{frame + 1:02d}.png")
        bpy.ops.render.render(write_still=True)


def main():
    global OUT, VARIANT
    names = list(ASSETS)
    args = sys.argv
    if "--" in args:
        extra = args[args.index("--") + 1 :]
        if "--variant" in extra:
            index = extra.index("--variant")
            VARIANT = extra[index + 1]
            del extra[index : index + 2]
        if "--out" in extra:
            index = extra.index("--out")
            OUT = Path(extra[index + 1])
            del extra[index : index + 2]
        if VARIANT not in STYLES:
            raise ValueError(f"Unknown variant: {VARIANT}")
        if extra:
            names = extra
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names:
        render_asset(name)


if __name__ == "__main__":
    main()
