"""Packaging regressions, including Linux-incompatible ZIP separators."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build", ROOT / "scripts" / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class BuildTests(unittest.TestCase):
    def test_package_matches_source_and_is_reproducible(self):
        info = json.loads((ROOT / "info.json").read_text())
        prefix = f"{info['name']}_{info['version']}/"
        with tempfile.TemporaryDirectory() as temp:
            first = build.build(output=Path(temp) / "first.zip")
            second = build.build(output=Path(temp) / "second.zip")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with ZipFile(first) as archive:
                names = archive.namelist()
                self.assertIn(prefix + "info.json", names)
                self.assertIn(prefix + "control.lua", names)
                self.assertEqual(len(names), len(set(names)))
                for name in names:
                    self.assertNotIn("\\", name)
                    self.assertTrue(name.startswith(prefix))
                    relative = name.removeprefix(prefix)
                    self.assertNotIn("..", Path(relative).parts)
                    self.assertEqual(archive.read(name), (ROOT / relative).read_bytes())
                expected = {prefix + p.relative_to(ROOT).as_posix()
                            for entry in build.PACKAGE_PATHS
                            for p in ((ROOT / entry).rglob("*") if (ROOT / entry).is_dir() else [ROOT / entry])
                            if p.is_file()}
                self.assertEqual(set(names), expected)


if __name__ == "__main__":
    unittest.main()
