from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]

ENTITY_NAMES = [
    "interstellar-lab",
    "quantum-replicator",
    "interstellar-dust-collector",
    "stellar-fusion-drive",
    "antimatter-drive",
    "interstellar-foundry",
    "interstellar-electromagnetic-plant",
    "interstellar-biochamber",
    "interstellar-cryogenic-plant",
]

ICON_NAMES = [
    "interstellar-dust",
    "ship-starter-pack",
    "antimatter",
    *ENTITY_NAMES,
]

TECH_NAMES = [
    "interstellar-fleets",
    "quantum-replication",
    "antimatter-containment",
    "interstellar-xenobiology",
    "quantum-fabrication",
    "orbital-industry",
    "fleet-printing",
    "interstellar-dust-crushing",
    "deep-dust-prospecting",
    "stellar-fusion-drive-efficiency",
    "antimatter-drive-efficiency",
    "interstellar-dust-collection-productivity",
    "quantum-replication-productivity",
    "fleet-coordination",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def assert_png(path: Path, size: tuple[int, int], alpha: bool, *, transparent: bool = False) -> None:
    require(path.exists(), f"missing {path}")
    with Image.open(path) as image:
        require(image.size == size, f"{path} has size {image.size}, expected {size}")
        require(image.format == "PNG", f"{path} is {image.format}, expected PNG")
        has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
        require(not alpha or has_alpha, f"{path} has no alpha channel")
        image.load()  # Decode the complete file, catching truncated IDAT data.
        if transparent:
            extrema = image.convert("RGBA").getchannel("A").getextrema()
            require(extrema[0] == 0 and extrema[1] > 0, f"{path} must contain transparent and visible pixels")


def assert_gif(path: Path) -> None:
    require(path.exists(), f"missing {path}")
    with Image.open(path) as image:
        require(image.format == "GIF", f"{path} is {image.format}, expected GIF")
        require(image.n_frames == 8, f"{path} has {image.n_frames} frames, expected 8")
        require(image.size == (256, 256), f"{path} has size {image.size}, expected (256, 256)")
        require(image.info.get("loop") == 0, f"{path} is not a looping preview")
        hashes = set()
        for index in range(image.n_frames):
            image.seek(index)
            require(image.info.get("duration", 0) > 0, f"{path} has a zero-duration frame")
            hashes.add(hashlib.sha256(image.convert("RGBA").tobytes()).digest())
        require(len(hashes) > 1, f"{path} has no visible animation")


def assert_ogg(path: Path) -> None:
    require(path.exists(), f"missing {path}")
    require(path.stat().st_size > 10_000, f"{path} is unexpectedly small")
    require(path.read_bytes()[:4] == b"OggS", f"{path} is not an OGG file")


def assert_sheet(path: Path, frame_size: tuple[int, int], frame_count: int, columns: int,
                 directions: int = 1, *, animated: bool = False, stable: bool = False) -> None:
    frame_width, frame_height = frame_size
    rows = math.ceil(frame_count / columns)
    assert_png(path, (frame_width * columns, frame_height * rows * directions), True, transparent=True)
    with Image.open(path) as sheet:
        for direction in range(directions):
            hashes = set()
            areas = []
            for index in range(frame_count):
                x = (index % columns) * frame_width
                y = (index // columns + direction * rows) * frame_height
                frame = sheet.crop((x, y, x + frame_width, y + frame_height)).convert("RGBA")
                alpha = frame.getchannel("A")
                bbox = alpha.point(lambda value: 255 if value > 8 else 0).getbbox()
                require(bbox is not None, f"{path}: direction {direction + 1} frame {index + 1} is empty")
                require(bbox[0] > 0 and bbox[1] > 0 and bbox[2] < frame_width and bbox[3] < frame_height,
                        f"{path}: direction {direction + 1} frame {index + 1} touches its cell edge ({bbox}); check clipped geometry")
                areas.append(sum(alpha.histogram()[9:]))
                hashes.add(hashlib.sha256(frame.tobytes()).digest())
            if animated:
                require(len(hashes) > 1, f"{path}: direction {direction + 1} animation frames are identical")
            if stable:
                require(min(areas) / max(areas) > 0.65,
                        f"{path}: visible silhouette area changes by over 35%; check missing geometry")


def mod_path(value: str) -> Path:
    relative = value.removeprefix("__interstellar-fleets__/")
    require(not Path(relative).is_absolute() and ".." not in Path(relative).parts, f"unsafe asset path: {value}")
    path = ROOT
    for component in Path(relative).parts:
        require(path.is_dir(), f"missing asset directory: {path}")
        require(component in {child.name for child in path.iterdir()}, f"missing or case-mismatched asset: {value}")
        path = path / component
    return path


def walk_tables(value, trail=""):
    if isinstance(value, dict):
        yield trail, value
        for key, child in value.items():
            yield from walk_tables(child, f"{trail}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_tables(child, f"{trail}[{index + 1}]")


def assert_prototypes(lua: str | None) -> dict:
    if lua:
        result = subprocess.run([lua, str(ROOT / "scripts" / "inspect_art_prototypes.lua")],
                                cwd=ROOT, capture_output=True, text=True, check=True)
        report = json.loads(result.stdout)
    else:
        try:
            from lupa.lua52 import LuaRuntime
        except ImportError as error:
            raise AssertionError("Install requirements-dev.txt or pass --lua /path/to/lua for the data-stage probe") from error
        runtime = LuaRuntime()
        output = []
        runtime.globals().print = output.append
        runtime.execute("package.path = ... .. '/?.lua;' .. package.path", ROOT.as_posix())
        runtime.execute("dofile(...)", str(ROOT / "scripts" / "inspect_art_prototypes.lua"))
        report = json.loads(output[-1])
    prototypes = report["prototypes"]
    manifest = report["manifest"]
    references = set()
    entities = {}
    for prototype in prototypes:
        label = f"{prototype['type']}/{prototype['name']}"
        if prototype["name"] in ENTITY_NAMES and prototype["type"] not in {"item", "recipe"}:
            entities[prototype["name"]] = prototype
        for trail, table in walk_tables(prototype, label):
            for field, value in table.items():
                if not isinstance(value, str) or not value.startswith("__interstellar-fleets__/"):
                    continue
                path = mod_path(value)
                references.add(path)
                require(path.is_file(), f"{trail}.{field} does not refer to a file")
                if path.suffix != ".png":
                    continue
                with Image.open(path) as image:
                    width, height = image.size
                if field in {"icon", "small_icon", "starmap_icon"}:
                    declared_size = table.get(f"{field}_size", table.get("icon_size"))
                    require(declared_size is not None, f"{trail}.{field} has no declared icon size")
                    require((width, height) == (declared_size, declared_size),
                            f"{trail}.{field} declares {declared_size}, actual image is {(width, height)}")
                elif field == "filename":
                    frame_width = table.get("width", table.get("size"))
                    frame_height = table.get("height", table.get("size"))
                    require(isinstance(frame_width, int) and isinstance(frame_height, int),
                            f"{trail} needs explicit integer sprite dimensions")
                    frames = table.get("frame_count", 1)
                    directions = table.get("direction_count", 1)
                    columns = table.get("line_length", frames)
                    require(frame_width > 0 and frame_height > 0 and frames > 0 and columns > 0,
                            f"{trail} has non-positive sprite dimensions")
                    rows = math.ceil(frames * directions / columns)
                    x, y = table.get("x", 0), table.get("y", 0)
                    require(x >= 0 and y >= 0 and x + min(columns, frames * directions) * frame_width <= width
                            and y + rows * frame_height <= height,
                            f"{trail} reads outside {(width, height)} sprite sheet")
                    require(table.get("scale", 1) > 0, f"{trail} has invalid scale")
                    require(all(1 <= value <= frames for value in table.get("frame_sequence", [])),
                            f"{trail} has out-of-range frame_sequence")
                    if path.name.endswith("-shadow.png"):
                        require(table.get("draw_as_shadow") is True, f"{trail} shadow layer lacks draw_as_shadow")
                        require("tint" not in table, f"{trail} incorrectly tints the shadow")
                    elif path.name.endswith("-glow.png"):
                        require(table.get("draw_as_glow") or table.get("draw_as_light"),
                                f"{trail} emission layer lacks a glow/light flag")
    for name in ENTITY_NAMES:
        require(name in entities, f"missing entity prototype: {name}")
        entity = entities[name]
        tables = [table for _, table in walk_tables(entity)]
        files = {table.get("filename") for table in tables}
        prefix = f"__interstellar-fleets__/graphics/entity/{name}/{name}"
        require(prefix + "-animation.png" in files, f"{name} does not use its Blender animation")
        require(prefix + "-glow.png" in files, f"{name} does not use its Blender emission layer")
        require(any(table.get("icon") == f"__interstellar-fleets__/graphics/icons/{name}.png" for table in tables),
                f"{name} does not use its Blender icon")
        custom_frames = [table.get("frame_count", 1) for table in tables
                         if table.get("filename") == prefix + "-animation.png"]
        for accent in entity.get("working_sound", {}).get("sound_accents", []):
            require(accent.get("frame", 0) < max(custom_frames),
                    f"{name} has a sound accent beyond its custom animation")
    collector = entities["interstellar-dust-collector"]["graphics_set"]
    for key in ("arm_head_animation", "arm_head_top_animation", "arm_link"):
        require(key in collector, f"collector lost its native {key}")
    for name in ("stellar-fusion-drive", "antimatter-drive"):
        entity = entities[name]
        require(entity["type"] == "simple-entity-with-owner", f"{name} must retain item-fueled drive behavior")
        require(entity.get("animations"), f"{name} has no custom drive animation")
        require(not entity.get("fuel_fluid_box") and not entity.get("oxidizer_fluid_box"),
                f"{name} accidentally inherited the vanilla thruster's fluid requirements")
    for name, entity in entities.items():
        graphics = entity.get("graphics_set", {})
        visuals = {entry.get("name") for entry in graphics.get("working_visualisations", [])}
        for _, table in walk_tables(entity.get("fluid_boxes", [])):
            for visual in table.get("enable_working_visualisations", []):
                require(visual in visuals, f"{name} has a disconnected pipe visual: {visual}")
    delivered = set((ROOT / "graphics" / "icons").glob("*.png"))
    delivered.update((ROOT / "graphics" / "technology").glob("*.png"))
    delivered.update((ROOT / "graphics" / "entity").glob("*/*.png"))
    require(not delivered - references, "unreferenced game art: " + ", ".join(str(path.relative_to(ROOT)) for path in sorted(delivered - references)))
    return report


def assert_animation_variation(body: Path, glow: Path, spec: dict) -> None:
    with Image.open(body) as body_image, Image.open(glow) as glow_image:
        width, height = spec["width"], spec["height"]
        rows = math.ceil(spec["frame_count"] / spec["line_length"])
        for direction in range(spec["directions"]):
            hashes = set()
            for index in range(spec["frame_count"]):
                x = index % spec["line_length"] * width
                y = (index // spec["line_length"] + direction * rows) * height
                box = (x, y, x + width, y + height)
                hashes.add(hashlib.sha256(body_image.crop(box).tobytes() + glow_image.crop(box).tobytes()).digest())
            require(len(hashes) > 1, f"{body}: direction {direction + 1} has no body or light animation")


def manifest_path(value: str, digest: str) -> Path:
    path = mod_path(value)
    require(path.is_file(), f"missing manifest asset: {path}")
    require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, f"stale provenance checksum for {path}")
    return path


def equal_metadata(left, right) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-9)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(equal_metadata(a, b) for a, b in zip(left, right))
    return left == right


def assert_blender_sources(models: list[Path], blender: str | None) -> None:
    for path in models:
        require(path.is_file(), f"missing editable Blender model: {path}")
        require(path.stat().st_size > 10_000, f"{path} is unexpectedly small")
        with path.open("rb") as handle:
            header = handle.read(12)
        require(header.startswith((b"BLENDER", b"\x1f\x8b", b"\x28\xb5\x2f\xfd")),
                f"{path} is not a Blender project or supported compressed Blender container")
    if blender is None:
        return
    with tempfile.TemporaryDirectory(prefix="factorio-art-blender-") as temporary:
        output = Path(temporary) / "scenes.json"
        result = subprocess.run([blender, "--background", "--factory-startup", "--disable-autoexec", "--python",
                                 str(ROOT / "scripts" / "inspect_blender_sources.py"), "--", "--output", str(output),
                                 *(str(path) for path in models)], capture_output=True, text=True)
        require(result.returncode == 0 and output.is_file(), f"Blender source inspection failed:\n{result.stderr}\n{result.stdout[-4000:]}")
        scenes = json.loads(output.read_text())
        require(len(scenes) == len(models), "Blender did not inspect every model")
        for scene in scenes:
            label = scene["path"]
            require(scene["mesh_objects"] >= 3, f"{label} has too little editable geometry")
            require(scene["materials"] >= 3, f"{label} has too few materials")
            require(scene["camera"] == "ORTHO", f"{label} has no orthographic render camera")
            require(scene["lights"] >= 1, f"{label} has no scene lighting")
            require(scene["transparent"], f"{label} render background is opaque")
            require(not scene["missing_dependencies"], f"{label} has missing dependencies: {scene['missing_dependencies']}")
            require(scene["linked_libraries"] == 0 and not scene["unpacked_images"],
                    f"{label} is not self-contained; pack linked geometry and image textures")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate delivered Blender art and actual Lua prototype references.")
    parser.add_argument("--lua", help="Use this Lua executable instead of the Lua 5.2 runtime in lupa")
    parser.add_argument("--blender", help="Also open every .blend and inspect its editable scene with this Blender executable")
    args = parser.parse_args()
    if args.lua is None:
        try:
            import lupa.lua52
        except ImportError:
            args.lua = shutil.which("lua")
    manifest_file = ROOT / "art" / "manifest.json"
    require(manifest_file.is_file(), "missing art/manifest.json; run the Blender renderer and asset packer")
    manifest = json.loads(manifest_file.read_text())
    require(manifest.get("schema_version") == 2, "art manifest must use schema_version 2")
    require(set(manifest["models"]) == set(ICON_NAMES), "model manifest does not contain exactly the twelve expected models")
    require(set(manifest["entities"]) == set(ENTITY_NAMES), "entity manifest does not contain exactly the nine expected machines")
    require(set(manifest["technologies"]) == set(TECH_NAMES), "technology manifest does not contain exactly the fourteen expected technologies")
    provenance = manifest.get("provenance", {})
    expected_sources = {
        "renderer": "scripts/blender_render_assets.py",
        "packer": "scripts/pack_blender_assets.py",
        "render_specification": "art/render-manifest.json",
    }
    require(set(provenance) == set(expected_sources), "art manifest must identify its renderer, packer, and render specification")
    for key, expected in expected_sources.items():
        require(provenance[key]["path"] == expected, f"incorrect {key} provenance path")
        manifest_path(provenance[key]["path"], provenance[key]["sha256"])

    report = assert_prototypes(args.lua)
    models = []
    for name, spec in manifest["models"].items():
        paths = {key: manifest_path(spec[key], spec["sha256"][key]) for key in ("blend", "hero", "sample", "icon")}
        models.append(paths["blend"])
        require(paths["blend"] == ROOT / "art" / "models" / f"{name}.blend", f"{name} must have its own editable model")
        assert_png(paths["hero"], (1024, 1024), True, transparent=True)
        assert_png(paths["sample"], (1200, 1000), False)
        assert_png(paths["icon"], (64, 64), True, transparent=True)
        require(spec["category"] == ("entity" if name in ENTITY_NAMES else "item"), f"{name} has incorrect model category")
    assert_blender_sources(models, args.blender)

    for name, spec in manifest["entities"].items():
        lua_spec = report["manifest"][name]
        for key in ("width", "height", "frame_count", "line_length", "directions", "scale", "shift", "animation_speed"):
            require(equal_metadata(spec[key], lua_spec[key]), f"{name}: JSON/Lua manifests disagree on {key}")
        require((spec["width"], spec["height"], spec["frame_count"], spec["line_length"]) == (512, 512, 8, 8),
                f"{name}: expected eight 512px frames in one row")
        require(spec["directions"] == (4 if name == "interstellar-dust-collector" else 1),
                f"{name}: incorrect number of directional views")
        paths = {key: manifest_path(spec[key], spec["sha256"][key]) for key in ("animation", "glow", "shadow", "preview")}
        for layer in ("animation", "glow", "shadow"):
            assert_sheet(paths[layer], (spec["width"], spec["height"]), spec["frame_count"],
                         spec["line_length"], spec["directions"], stable=layer == "animation")
        assert_animation_variation(paths["animation"], paths["glow"], spec)
        assert_gif(paths["preview"])

    technology_pixels = set()
    for name, spec in manifest["technologies"].items():
        path = manifest_path(spec["path"], spec["sha256"])
        assert_png(path, (128, 128), True)
        require(spec["source_models"] and set(spec["source_models"]) <= set(ICON_NAMES), f"{name} has missing model provenance")
        require(spec["glyph"], f"{name} has no identifying technology glyph")
        with Image.open(path) as image:
            technology_pixels.add(hashlib.sha256(image.convert("RGBA").tobytes()).digest())
    require(len(technology_pixels) == len(TECH_NAMES), "technology icons include duplicate artwork")

    for key in ("contact_sheet", "key_art", "thumbnail"):
        spec = manifest["presentation"][key]
        path = manifest_path(spec["path"], spec["sha256"])
        assert_png(path, (spec["width"], spec["height"]), False)
    require(manifest["presentation"]["key_art"]["width"] == 1600 and manifest["presentation"]["key_art"]["height"] == 1000,
            "key art must be 1600x1000")
    assert_ogg(ROOT / "sound" / "interstellar-lab-working.ogg")
    print(f"Art validation passed: {len(models)} editable models and samples, 27 sprite layers, "
          f"12 icons, 14 unique technology images, 9 animated previews; {len(report['prototypes'])} offline prototypes inspected.")
    print("Blender scene inspection passed." if args.blender else "Blender file headers checked; use --blender for scene inspection.")
    print("This offline probe does not replace a Factorio engine load/placement smoke test.")


if __name__ == "__main__":
    main()
