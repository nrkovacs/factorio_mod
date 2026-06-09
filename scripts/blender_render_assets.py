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
    if color[3] < 1:
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
        mat.show_transparent_back = False
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


def add_cone(name, location, radius1, radius2, depth, mat, vertices=5, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("facet bevel", "BEVEL")
    bevel.width = 0.015
    bevel.segments = 1
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
    for x in (-0.38, 0.38):
        add_panel("hazard_mark", (x, -0.91, 0.25), (0.2, 0.035, 0.045), rust)


def add_radiator_bank(side: float, primary, trim, accent):
    add_panel("radiator_back", (side * 1.08, 0.06, 0.88), (0.08, 1.1, 0.55), trim)
    for index, y in enumerate((-0.42, -0.18, 0.06, 0.30, 0.54)):
        add_panel("radiator_fin", (side * 1.18, y, 0.88), (0.08, 0.13, 0.48), primary if index % 2 else trim)
    add_uv_sphere("radiator_pin", (side * 1.22, -0.58, 1.17), 0.04, accent)


def add_sensor_cluster(accent, trim):
    for index, x in enumerate((-0.56, -0.28, 0.28, 0.56)):
        add_cylinder("sensor_stalk", (x, 0.58, 1.35 + 0.05 * (index % 2)), 0.018, 0.34, trim)
        add_uv_sphere("sensor_eye", (x, 0.58, 1.55 + 0.05 * (index % 2)), 0.05, accent)


def add_crystal_cluster(accent, trim, origin=(0, 0, 1.45), scale=1.0):
    offsets = [(-0.16, 0.02, 0.0, 0.22), (0.0, -0.02, 0.08, 0.28), (0.17, 0.04, 0.02, 0.2)]
    for x, y, z, height in offsets:
        add_cone(
            "crystal_shard",
            (origin[0] + x * scale, origin[1] + y * scale, origin[2] + z * scale),
            0.07 * scale,
            0.015 * scale,
            height * scale,
            accent,
            vertices=5,
            rotation=(0.18, 0.08, 0.4),
        )
    add_panel("crystal_mount", (origin[0], origin[1], origin[2] - 0.14 * scale), (0.48 * scale, 0.28 * scale, 0.07 * scale), trim)


def add_satellite_dish(name, location, trim, accent, rotation_z=0.0):
    dish = add_torus(name, location, 0.21, 0.014, trim, rotation=(1.05, 0, rotation_z))
    dish.scale.z = 0.35
    add_cylinder(f"{name}_mast", (location[0], location[1], location[2] - 0.24), 0.028, 0.42, trim)
    add_uv_sphere(f"{name}_feed", (location[0] + math.cos(rotation_z) * 0.15, location[1] + math.sin(rotation_z) * 0.15, location[2] + 0.02), 0.04, accent)


def add_solar_wing(name, side: float, y: float, metal, primary, trim):
    add_cylinder(f"{name}_boom", (side * 1.22, y, 0.86), 0.025, 0.78, trim, vertices=12, rotation=(math.pi / 2, 0, 0))
    for row, z in enumerate((0.72, 0.94)):
        for column, offset in enumerate((-0.18, 0.0, 0.18)):
            panel = add_panel(
                f"{name}_panel",
                (side * 1.5, y + offset, z),
                (0.26, 0.13, 0.035),
                primary if (row + column) % 2 else metal,
            )
            panel.rotation_euler[2] = side * 0.12
    add_panel(f"{name}_spine", (side * 1.34, y, 0.83), (0.04, 0.5, 0.05), trim)


def add_hex_dome_pattern(accent, trim, pulse: float):
    for ring, radius in enumerate((0.0, 0.2, 0.4)):
        count = 1 if ring == 0 else 6 * ring
        for index in range(count):
            angle = 0 if count == 1 else index * math.tau / count
            x = math.cos(angle) * radius
            y = -0.05 + math.sin(angle) * radius * 0.72
            z = 1.42 + max(0, 0.24 - radius * 0.18)
            add_cylinder(
                "dome_hex",
                (x, y, z),
                0.055 if ring else 0.07,
                0.012,
                accent if pulse > 0.35 else trim,
                vertices=6,
                rotation=(0, 0, angle + math.pi / 6),
            )


def add_reference_lab(primary, accent, dark, metal, trim, rust, frame: int, angle: float):
    pulse = [0.08, 0.55, 0.92, 0.35][frame]
    dome_glass = material("dome_glass", (0.18 + pulse * 0.2, 0.46 - pulse * 0.08, 0.74 + pulse * 0.18, 0.5), 0.15 + pulse * 0.55)
    purple = material("research_purple", (0.68, 0.24, 1.0, 1), 0.65 + pulse * 1.45)
    cyan = material("platform_cyan", (0.0, 0.95, 0.95, 1), 1.4)
    steam = material("steam", (0.85, 0.9, 0.92, 0.42), 0.05)

    add_cube("platform_deck", (0, -0.03, 0.16), (2.55, 2.05, 0.24), dark)
    add_panel("front_platform_lip", (0, -1.12, 0.3), (2.35, 0.08, 0.13), trim)
    add_panel("rear_platform_lip", (0, 0.98, 0.3), (2.1, 0.08, 0.12), trim)
    for x in (-0.85, 0, 0.85):
        add_panel("deck_trace", (x, -0.98, 0.36), (0.06, 0.18, 0.035), cyan)
    for x in (-1.05, 1.05):
        add_panel("side_teal_conduit", (x, -0.34, 0.42), (0.055, 0.88, 0.045), cyan)
        add_panel("corner_teal_conduit", (x * 0.72, -0.96, 0.42), (0.5, 0.045, 0.04), cyan)

    add_cube("lab_octagonal_body", (0, -0.05, 0.72), (1.48, 1.22, 0.55), metal)
    add_panel("front_window_band", (0, -0.7, 0.8), (1.05, 0.05, 0.18), accent)
    for x in (-0.58, -0.28, 0.28, 0.58):
        add_panel("window_pane", (x, -0.735, 0.82), (0.14, 0.025, 0.12), cyan)
    for side in (-1, 1):
        add_panel("buttress", (side * 0.86, -0.26, 0.7), (0.18, 0.72, 0.48), trim)
        add_cylinder("corner_vessel", (side * 0.96, -0.68, 0.63), 0.09, 0.42, rust)
        add_solar_wing("solar_wing", side, 0.46, metal, primary, trim)

    add_cylinder("dome_socket", (0, -0.05, 1.08), 0.58, 0.16, trim)
    dome = add_uv_sphere("research_dome", (0, -0.05, 1.28), 0.56, dome_glass)
    dome.scale.z = 0.42
    add_torus("dome_rim", (0, -0.05, 1.13), 0.58, 0.03, trim)
    add_hex_dome_pattern(purple if pulse > 0.4 else accent, trim, pulse)
    add_uv_sphere("research_core", (0.05 * math.cos(angle), -0.05 + 0.05 * math.sin(angle), 1.28), 0.19 + pulse * 0.09, purple)
    add_torus("research_scan_ring", (0, -0.05, 1.31), 0.42, 0.018, purple, rotation=(0.35, 0.15, angle))

    add_satellite_dish("dish_left", (-0.52, 0.66, 1.42), trim, accent, rotation_z=2.45)
    add_satellite_dish("dish_right", (0.48, 0.68, 1.5), trim, accent, rotation_z=0.85)
    add_sensor_cluster(accent, trim)
    for x in (-0.74, 0.74):
        add_cylinder("rear_antenna", (x, 0.62, 1.15), 0.02, 0.52, trim)
        add_uv_sphere("rear_beacon", (x, 0.62, 1.45), 0.045 + pulse * 0.02, cyan)

    if frame in {2, 3}:
        for index, x in enumerate((-0.86, 0.86, -0.35, 0.35)):
            y = -0.82 if index < 2 else 0.78
            add_uv_sphere("steam_puff", (x, y, 0.66 + 0.12 * index), 0.13 + 0.04 * frame, steam)
            add_uv_sphere("steam_puff_high", (x + 0.04 * math.sin(angle), y, 0.88 + 0.08 * index), 0.09 + 0.03 * frame, steam)


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

    kind = spec["kind"]
    angle = frame * math.tau / 4

    if kind != "lab":
        add_cylinder("base", (0, 0, 0.15), 1.05, 0.3, dark)
        add_cube("body", (0, 0, 0.65), (1.8, 1.45, 0.8), metal)
        add_cube("front_panel", (0, -0.78, 0.72), (1.2, 0.12, 0.5), primary)
        add_machine_greebles(primary, accent, dark, trim, rust)

    if kind in {"lab", "replicator"}:
        if kind == "lab":
            add_reference_lab(primary, accent, dark, metal, trim, rust, frame, angle)
        else:
            add_torus("energy_ring", (0, -0.15, 1.26), 0.48, 0.035, primary, rotation=(0.35, 0.15, angle))
            add_uv_sphere("core", (0, -0.15, 1.25), 0.42, accent)
            add_cylinder("core_socket", (0, -0.15, 1.08), 0.5, 0.12, trim)
            add_radiator_bank(-1, primary, trim, accent)
            add_radiator_bank(1, primary, trim, accent)
            for i in range(6):
                a = angle + i * math.tau / 6
                add_cylinder("core_arm", (math.cos(a) * 0.55, math.sin(a) * 0.55, 1.18), 0.04, 0.58, primary, vertices=16, rotation=(math.pi / 2, 0, a))
            add_torus("matter_ring", (0, -0.15, 1.42), 0.32, 0.025, accent, rotation=(math.pi / 2, 0, -angle))
            add_torus("outer_matter_gate", (0, -0.15, 1.42), 0.56, 0.02, primary, rotation=(math.pi / 2, 0, angle * 0.5))
            add_crystal_cluster(accent, trim, origin=(0, -0.2, 1.72), scale=0.75)
            for i in range(3):
                a = angle * 0.5 + i * math.tau / 3
                add_uv_sphere("replication_particle", (math.cos(a) * 0.36, math.sin(a) * 0.36 - 0.15, 1.58), 0.055, accent)
    elif kind == "collector":
        add_cylinder("collector_mast", (0, -0.05, 1.24), 0.075, 0.78, trim)
        add_torus("collector_field", (0, -0.05, 1.42), 0.5, 0.018, accent, rotation=(0.2, 0.7, angle))
        add_torus("wide_dust_net", (0, -0.05, 1.2), 0.78, 0.014, primary, rotation=(0.35, 0.8, -angle))
        for x in (-0.48, 0.48):
            add_panel("collector_solar_wing", (x, 0.64, 0.95), (0.42, 0.08, 0.32), primary)
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
        for side in (-1, 1):
            add_cone("drive_keel", (side * 0.9, 0.15, 1.0), 0.18, 0.02, 0.55, trim, vertices=3, rotation=(0, math.pi / 2, side * 0.55))
            add_panel("drive_heat_shield", (side * 0.86, -0.62, 0.35), (0.32, 0.22, 0.08), rust)
        add_cylinder("fuel_line_l", (-0.42, -0.06, 1.04), 0.04, 0.86, trim, vertices=16, rotation=(math.pi / 2, 0, 0))
        add_cylinder("fuel_line_r", (0.42, -0.06, 1.04), 0.04, 0.86, trim, vertices=16, rotation=(math.pi / 2, 0, 0))
        for x in (-0.48, 0, 0.48):
            add_cylinder("exhaust_ring", (x, -1.07, 0.62), 0.11, 0.1, rust, vertices=24, rotation=(math.pi / 2, 0, 0))
            add_cone("plasma_feather", (x, -1.24, 0.62), 0.05 + 0.01 * frame, 0.17, 0.32, accent, vertices=24, rotation=(math.pi / 2, 0, 0))
        add_torus("drive_containment", (0, -0.02, 1.06), 0.42, 0.035, accent, rotation=(0.1, 0.7, angle))
    elif kind == "foundry":
        add_cylinder("furnace", (0, -0.1, 1.2), 0.48, 0.55, primary)
        add_uv_sphere("molten_core", (0, -0.1, 1.3), 0.28 + 0.03 * math.sin(angle), accent)
        add_cylinder("chimney_l", (-0.54, 0.28, 1.28), 0.12, 0.62, dark)
        add_cylinder("chimney_r", (0.54, 0.28, 1.18), 0.1, 0.48, dark)
        add_torus("molten_lip", (0, -0.1, 1.46), 0.42, 0.035, rust)
        for x in (-0.44, 0.44):
            add_cone("slag_crane", (x, -0.46, 1.42), 0.055, 0.02, 0.5, trim, vertices=4, rotation=(0.25, 0.1, x))
            add_uv_sphere("slag_drop", (x * 0.8, -0.58, 1.12), 0.07, accent)
        add_panel("ore_loader", (0, 0.72, 0.92), (1.0, 0.18, 0.22), rust)
    elif kind == "electromagnetic":
        for x in (-0.45, 0, 0.45):
            add_cylinder("coil", (x, -0.08, 1.2), 0.22, 0.5, primary, rotation=(math.pi / 2, 0, 0))
            add_cylinder("coil_core", (x, -0.08, 1.2), 0.1, 0.58, trim, vertices=24, rotation=(math.pi / 2, 0, 0))
            add_torus("coil_binding", (x, -0.08, 1.2), 0.24, 0.012, rust, rotation=(math.pi / 2, 0, angle))
        add_cylinder("arc", (0, -0.08, 1.2), 0.08, 1.25, accent, rotation=(0, math.pi / 2, angle))
        add_cylinder("diagonal_arc", (0, -0.08, 1.32), 0.035, 1.05, accent, vertices=16, rotation=(0.7, math.pi / 2, -angle))
        for x in (-0.72, 0.72):
            add_cylinder("tesla_post", (x, 0.28, 1.22), 0.045, 0.58, trim)
            add_uv_sphere("tesla_cap", (x, 0.28, 1.54), 0.09, accent)
    elif kind == "biochamber":
        add_torus("bio_tank_rim", (0, -0.05, 1.22), 0.44, 0.035, trim)
        add_uv_sphere("bio_core", (0, -0.05, 1.22), 0.42, primary)
        add_torus("bio_glass_equator", (0, -0.05, 1.22), 0.48, 0.018, accent, rotation=(math.pi / 2, 0, angle))
        for x in (-0.54, 0.54):
            add_cylinder("nutrient_tank", (x, 0.24, 1.06), 0.14, 0.42, trim)
            add_cylinder("nutrient_line", (x * 0.58, 0.0, 1.08), 0.025, 0.62, accent, vertices=12, rotation=(math.pi / 2, 0, x))
        add_uv_sphere("bio_pulse", (0.2 * math.cos(angle), -0.05 + 0.2 * math.sin(angle), 1.34), 0.12 + 0.04 * frame, accent)
        add_uv_sphere("bio_bubble", (-0.26, -0.12, 1.18 + 0.06 * math.sin(angle)), 0.08 + 0.02 * (3 - frame), accent)
    elif kind == "cryogenic":
        add_cylinder("cryo_tank_l", (-0.42, -0.05, 1.16), 0.22, 0.72, primary)
        add_cylinder("cryo_tank_r", (0.42, -0.05, 1.16), 0.22, 0.72, primary)
        add_cylinder("cryo_tank_center", (0, 0.15, 1.06), 0.18, 0.62, trim)
        add_uv_sphere("frost_core", (0, -0.08, 1.26), 0.26, accent)
        add_uv_sphere("cold_vapor", (0.2 * math.cos(angle), -0.25 + 0.12 * math.sin(angle), 1.55), 0.11, accent)
        add_cylinder("cryo_pipe", (0, 0.28, 1.1), 0.05, 1.1, trim, vertices=16, rotation=(math.pi / 2, 0, math.pi / 2))
        add_torus("frost_ring", (0, -0.08, 1.28), 0.32, 0.025, accent, rotation=(math.pi / 2, 0, angle))
        add_crystal_cluster(accent, trim, origin=(0, -0.38, 1.34), scale=0.7)

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
