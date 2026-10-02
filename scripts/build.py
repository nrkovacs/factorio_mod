"""Build a deterministic, cross-platform Factorio mod archive."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PATHS = (
    "control.lua", "data.lua", "info.json", "thumbnail.png", "README.md",
    "docs", "graphics", "locale", "prototypes", "sound", "wiki",
)


def build(root: Path = ROOT, output: Path | None = None) -> Path:
    info = json.loads((root / "info.json").read_text(encoding="utf-8"))
    package = f"{info['name']}_{info['version']}"
    output = output or root / "dist" / f"{package}.zip"
    files = []
    for name in PACKAGE_PATHS:
        path = root / name
        if not path.exists():
            raise FileNotFoundError(f"Missing required package input: {path}")
        if path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file())
        else:
            files.append(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".zip.tmp")
    try:
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(files):
                # ZIP paths are POSIX on every OS. Compress-Archive on Windows
                # wrote backslashes that Linux Factorio could not load.
                entry = ZipInfo(f"{package}/{path.relative_to(root).as_posix()}", (1980, 1, 1, 0, 0, 0))
                entry.compress_type = ZIP_DEFLATED
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, path.read_bytes(), compresslevel=9)
        temporary.replace(output)
    finally:
        if temporary.exists():
            temporary.unlink()
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Override the release ZIP path")
    print(build(output=parser.parse_args().output))
