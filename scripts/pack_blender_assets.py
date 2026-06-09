from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
RENDERS = ROOT / "tmp" / "blender-renders"
REFERENCE_SOURCES = ROOT / "graphics" / "source"
ICONS = ROOT / "graphics" / "icons"
TECH = ROOT / "graphics" / "technology"
ENTITY = ROOT / "graphics" / "entity"
PREVIEWS = ROOT / "graphics" / "previews"

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

ENTITY_FRAME_SIZES = {
    "interstellar-lab": 256,
}

TECH_ALIASES = {
    "interstellar-fleets": "interstellar-lab",
    "quantum-replication": "quantum-replicator",
    "antimatter-containment": "antimatter-drive",
    "interstellar-xenobiology": "interstellar-biochamber",
    "quantum-fabrication": "quantum-replicator",
    "orbital-industry": "interstellar-foundry",
    "fleet-printing": "stellar-fusion-drive",
    "interstellar-dust-crushing": "interstellar-dust-collector",
    "deep-dust-prospecting": "interstellar-dust-collector",
    "stellar-fusion-drive-efficiency": "stellar-fusion-drive",
    "antimatter-drive-efficiency": "antimatter-drive",
    "interstellar-dust-collection-productivity": "interstellar-dust-collector",
    "quantum-replication-productivity": "quantum-replicator",
    "fleet-coordination": "stellar-fusion-drive",
}

ICON_ALIASES = {
    "interstellar-dust": "interstellar-dust-collector",
    "ship-starter-pack": "stellar-fusion-drive",
    "antimatter": "antimatter-drive",
}


def trim_alpha(image: Image.Image) -> Image.Image:
    bbox = image.getbbox()
    if not bbox:
        return image
    return image.crop(bbox)


def fit_square(image: Image.Image, size: int, padding: int = 6) -> Image.Image:
    image = trim_alpha(image.convert("RGBA"))
    image.thumbnail((size - padding * 2, size - padding * 2), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(image, ((size - image.width) // 2, (size - image.height) // 2))
    return out


def polish(image: Image.Image, contrast: float = 1.12, sharpness: float = 1.25) -> Image.Image:
    alpha = image.getchannel("A")
    rgb = Image.new("RGBA", image.size, (0, 0, 0, 0))
    color = ImageEnhance.Contrast(image.convert("RGB")).enhance(contrast)
    color = ImageEnhance.Sharpness(color).enhance(sharpness)
    rgb.paste(color.convert("RGBA"), mask=alpha)
    return rgb


def frame_size_for(name: str) -> int:
    return ENTITY_FRAME_SIZES.get(name, 128)


def load_frames(name: str, size: int | None = None) -> list[Image.Image]:
    size = size or frame_size_for(name)
    frames = []
    for index in range(1, 5):
        reference_path = REFERENCE_SOURCES / f"{name}-reference" / f"frame_{index:02d}.png"
        path = reference_path if reference_path.exists() else RENDERS / name / f"frame_{index:02d}.png"
        if not path.exists():
            raise FileNotFoundError(path)
        frame = polish(fit_square(Image.open(path), size, padding=4))
        frames.append(frame)
    return frames


def glow_from_frame(frame: Image.Image) -> Image.Image:
    alpha = frame.getchannel("A")
    glow_alpha = alpha.filter(ImageFilter.GaussianBlur(max(8, frame.width // 16)))
    glow = Image.new("RGBA", frame.size, (105, 215, 255, 0))
    glow.putalpha(glow_alpha.point(lambda value: int(value * 0.55)))
    return glow


def preview_frame(frame: Image.Image, index: int) -> Image.Image:
    out = fit_square(frame, 128, padding=2)
    sparkle = Image.new("RGBA", out.size, (0, 0, 0, 0))
    angle = index * math.tau / 4
    x = int(out.width / 2 + math.cos(angle + 0.4) * 42)
    y = int(out.height / 2 + math.sin(angle + 0.4) * 30 - 12)
    for radius, alpha in [(4, 90), (2, 180), (1, 255)]:
        dot = Image.new("RGBA", (radius * 2 + 1, radius * 2 + 1), (125, 225, 255, alpha))
        sparkle.alpha_composite(dot, (x - radius, y - radius))
    out.alpha_composite(sparkle)
    return out


def save_sheet(name: str, frames: list[Image.Image]) -> None:
    directory = ENTITY / name
    directory.mkdir(parents=True, exist_ok=True)
    frame_size = frames[0].width
    sheet = Image.new("RGBA", (frame_size * 4, frame_size), (0, 0, 0, 0))
    glow_sheet = Image.new("RGBA", (frame_size * 4, frame_size), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, (index * frame_size, 0))
        glow_sheet.alpha_composite(glow_from_frame(frame), (index * frame_size, 0))
    sheet.save(directory / f"{name}-animation.png")
    glow_sheet.save(directory / f"{name}-glow.png")
    preview_frames = [preview_frame(frame, index) for index, frame in enumerate(frames)]
    preview_frames[0].save(
        PREVIEWS / f"{name}.gif",
        save_all=True,
        append_images=preview_frames[1:],
        duration=160,
        loop=0,
        disposal=2,
    )


def save_icon(name: str, source: str) -> None:
    frame = load_frames(source, 96)[0]
    icon = fit_square(frame, 64, padding=4)
    icon = ImageEnhance.Sharpness(icon).enhance(1.3)
    ICONS.mkdir(parents=True, exist_ok=True)
    icon.save(ICONS / f"{name}.png")


def save_tech(name: str, source: str) -> None:
    frame = load_frames(source, 112)[0]
    out = Image.new("RGBA", (128, 128), (14, 18, 26, 255))
    for i in range(18):
        x = (i * 47) % 128
        y = (i * 29) % 128
        out.alpha_composite(Image.new("RGBA", (4, 4), (115, 205, 255, 130)), (x, y))
    out.alpha_composite(glow_from_frame(fit_square(frame, 128, padding=4)))
    out.alpha_composite(fit_square(frame, 112, padding=0), (8, 8))
    out = polish(out, contrast=1.08, sharpness=1.12)
    TECH.mkdir(parents=True, exist_ok=True)
    out.save(TECH / f"{name}.png")


def save_preview_sheet() -> None:
    names = ["interstellar-dust", "ship-starter-pack", "antimatter", *ENTITY_NAMES]
    cell = 96
    cols = 4
    rows = math.ceil(len(names) / cols)
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (16, 20, 24, 255))
    for index, name in enumerate(names):
        icon = Image.open(ICONS / f"{name}.png").convert("RGBA")
        x = (index % cols) * cell
        y = (index // cols) * cell
        sheet.alpha_composite(icon, (x + 16, y + 8))
    sheet.save(ROOT / "graphics" / "art-preview-sheet.png")


def main() -> None:
    for directory in [ICONS, TECH, ENTITY, PREVIEWS]:
        directory.mkdir(parents=True, exist_ok=True)
    for name in ENTITY_NAMES:
        frames = load_frames(name)
        save_sheet(name, frames)
        save_icon(name, name)
    for icon_name, source in ICON_ALIASES.items():
        save_icon(icon_name, source)
    for tech_name, source in TECH_ALIASES.items():
        save_tech(tech_name, source)
    save_preview_sheet()
    print("Packed Blender renders into Factorio assets")


if __name__ == "__main__":
    main()
