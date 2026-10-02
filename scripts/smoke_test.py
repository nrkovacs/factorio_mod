"""Validate the built ZIP and real fleet operations using a headless Factorio binary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from build import ROOT, build


def run(binary: Path, arguments: list[str], log: Path, required: str) -> None:
    result = subprocess.run([str(binary), *arguments], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write_text(result.stdout, encoding="utf-8")
    print(result.stdout, end="", flush=True)
    if result.returncode or required not in result.stdout or "Mod package read error" in result.stdout:
        raise RuntimeError(f"Factorio validation failed; see {log}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("factorio", type=Path, help="Path to Factorio 2.0 headless executable")
    parser.add_argument("--output", type=Path, default=ROOT / "validation")
    args = parser.parse_args()
    binary = args.factorio.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    mods = output / "mods"
    mods.mkdir(exist_ok=True)
    info = json.loads((ROOT / "info.json").read_text())
    archive = build(output=mods / f"{info['name']}_{info['version']}.zip")
    companion = mods / "interstellar-fleets-validation_0.1.0"
    shutil.copytree(ROOT / "tests" / "factorio", companion, dirs_exist_ok=True)
    (mods / "mod-list.json").write_text(json.dumps({"mods": [
        {"name": name, "enabled": True} for name in
        ("base", "quality", "elevated-rails", "space-age", "interstellar-fleets", "interstellar-fleets-validation")
    ]}), encoding="utf-8")
    userdata = output / "userdata"
    userdata.mkdir(exist_ok=True)
    # Factorio's distributed executable is bin/x64/factorio.
    data = binary.parents[2] / "data"
    config = output / "config.ini"
    config.write_text(f"[path]\nread-data={data.as_posix()}\nwrite-data={userdata.as_posix()}\n", encoding="utf-8")
    common = ["--config", str(config), "--mod-directory", str(mods)]
    save = output / "regression.zip"
    run(binary, [*common, "--create", str(save)], output / "create.log", f"Loading mod interstellar-fleets {info['version']}")
    if "INTERSTELLAR_FLEETS_PROTOTYPE_TESTS_PASSED" not in (output / "create.log").read_text():
        raise RuntimeError("Factorio data-stage regression marker missing")
    run(binary, [*common, "--benchmark", str(save), "--benchmark-ticks", "600", "--benchmark-runs", "1"],
        output / "runtime.log", "INTERSTELLAR_FLEETS_RUNTIME_TESTS_PASSED")
    print(f"Real Factorio validation passed for {archive}")


if __name__ == "__main__":
    main()
