"""Open every delivered model in Blender and inspect its editable scene.

Used by validate_art_assets.py --blender <executable>; never renders or saves.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("models", type=Path, nargs="+")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])
    results = []
    for path in args.models:
        bpy.ops.wm.open_mainfile(filepath=str(path.resolve()), load_ui=False, use_scripts=False)
        scene = bpy.context.scene
        missing = []
        unpacked_images = []
        for library in bpy.data.libraries:
            if not Path(bpy.path.abspath(library.filepath)).exists():
                missing.append(library.filepath)
        for image in bpy.data.images:
            if image.source == "FILE" and not image.packed_file:
                unpacked_images.append(image.filepath)
                if not Path(bpy.path.abspath(image.filepath)).exists():
                    missing.append(image.filepath)
        results.append({
            "path": str(path.resolve()),
            "mesh_objects": sum(obj.type == "MESH" for obj in scene.objects),
            "lights": sum(obj.type == "LIGHT" for obj in scene.objects),
            "materials": len(bpy.data.materials),
            "camera": scene.camera.data.type if scene.camera else None,
            "transparent": scene.render.film_transparent,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y],
            "missing_dependencies": missing,
            "linked_libraries": len(bpy.data.libraries),
            "unpacked_images": unpacked_images,
        })
    args.output.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
