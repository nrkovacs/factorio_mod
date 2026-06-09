from __future__ import annotations

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


def assert_png(path: Path, size: tuple[int, int], alpha: bool) -> None:
    require(path.exists(), f"missing {path}")
    with Image.open(path) as image:
        require(image.size == size, f"{path} has size {image.size}, expected {size}")
        require(image.format == "PNG", f"{path} is {image.format}, expected PNG")
        has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
        require(has_alpha == alpha or has_alpha, f"{path} alpha={has_alpha}, expected alpha={alpha}")


def assert_gif(path: Path) -> None:
    require(path.exists(), f"missing {path}")
    with Image.open(path) as image:
        require(image.format == "GIF", f"{path} is {image.format}, expected GIF")
        require(image.n_frames == 4, f"{path} has {image.n_frames} frames, expected 4")
        require(image.size == (128, 128), f"{path} has size {image.size}, expected (128, 128)")


def assert_ogg(path: Path) -> None:
    require(path.exists(), f"missing {path}")
    require(path.stat().st_size > 10_000, f"{path} is unexpectedly small")
    require(path.read_bytes()[:4] == b"OggS", f"{path} is not an OGG file")


def main() -> None:
    for name in ICON_NAMES:
        assert_png(ROOT / "graphics" / "icons" / f"{name}.png", (64, 64), True)

    for name in TECH_NAMES:
        assert_png(ROOT / "graphics" / "technology" / f"{name}.png", (128, 128), True)

    for name in ENTITY_NAMES:
        entity_dir = ROOT / "graphics" / "entity" / name
        assert_png(entity_dir / f"{name}-animation.png", (512, 128), True)
        assert_png(entity_dir / f"{name}-glow.png", (512, 128), True)
        assert_gif(ROOT / "graphics" / "previews" / f"{name}.gif")

    assert_png(ROOT / "graphics" / "art-preview-sheet.png", (384, 288), True)
    assert_ogg(ROOT / "sound" / "interstellar-lab-working.ogg")
    print("Art asset validation passed")


if __name__ == "__main__":
    main()
