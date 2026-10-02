"""Run syntax checks and regression tests without a Factorio installation."""
from pathlib import Path
import os
import subprocess
import sys

from lupa.lua52 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
syntax = LuaRuntime()
for path in [ROOT / "control.lua", ROOT / "data.lua", *sorted((ROOT / "prototypes").glob("*.lua"))]:
    syntax.execute("assert(loadfile(...))", str(path))
print("Lua 5.2 syntax checks passed", flush=True)
for path in sorted((ROOT / "tests").glob("test_*.lua")):
    print(f"Running {path.relative_to(ROOT)}", flush=True)
    LuaRuntime().execute("dofile(...)", str(path))
subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"], check=True)
subprocess.run([sys.executable, "scripts/validate_art_assets.py"], check=True)
