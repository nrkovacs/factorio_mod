from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "graphics" / "icons"
TECH = ROOT / "graphics" / "technology"
ENTITY = ROOT / "graphics" / "entity"
PREVIEWS = ROOT / "graphics" / "previews"


ASSETS = {
    "interstellar-dust": {
        "title": "Interstellar Dust",
        "palette": ((255, 211, 86), (110, 225, 255), (255, 255, 196)),
        "kind": "orb",
    },
    "ship-starter-pack": {
        "title": "Ship Starter Pack",
        "palette": ((106, 190, 255), (255, 218, 108), (205, 225, 245)),
        "kind": "crate",
    },
    "antimatter": {
        "title": "Antimatter",
        "palette": ((206, 100, 255), (109, 228, 255), (255, 255, 255)),
        "kind": "capsule",
    },
    "interstellar-lab": {
        "title": "Interstellar Lab",
        "palette": ((84, 230, 255), (72, 99, 148), (242, 255, 255)),
        "kind": "lab",
    },
    "quantum-replicator": {
        "title": "Quantum Replicator",
        "palette": ((190, 100, 255), (96, 72, 142), (255, 239, 255)),
        "kind": "replicator",
    },
    "interstellar-dust-collector": {
        "title": "Dust Collector",
        "palette": ((255, 205, 66), (98, 110, 126), (255, 255, 190)),
        "kind": "collector",
    },
    "stellar-fusion-drive": {
        "title": "Fusion Drive",
        "palette": ((86, 210, 255), (55, 82, 130), (235, 255, 255)),
        "kind": "drive",
    },
    "antimatter-drive": {
        "title": "Antimatter Drive",
        "palette": ((210, 96, 255), (75, 52, 118), (255, 236, 255)),
        "kind": "drive",
    },
    "interstellar-foundry": {
        "title": "Interstellar Foundry",
        "palette": ((255, 128, 58), (92, 91, 96), (255, 219, 146)),
        "kind": "foundry",
    },
    "interstellar-electromagnetic-plant": {
        "title": "Interstellar Electromagnetic Plant",
        "palette": ((198, 94, 255), (69, 81, 135), (126, 238, 255)),
        "kind": "electromagnetic",
    },
    "interstellar-biochamber": {
        "title": "Interstellar Biochamber",
        "palette": ((94, 235, 128), (63, 98, 76), (220, 255, 188)),
        "kind": "biochamber",
    },
    "interstellar-cryogenic-plant": {
        "title": "Interstellar Cryogenic Plant",
        "palette": ((118, 222, 255), (63, 78, 126), (235, 255, 255)),
        "kind": "cryogenic",
    },
    "fleet-printing": {
        "title": "Fleet Printing",
        "palette": ((106, 190, 255), (255, 218, 108), (205, 225, 245)),
        "kind": "fleet",
    },
    "interstellar-fleets": {
        "title": "Interstellar Fleets",
        "palette": ((84, 230, 255), (255, 205, 66), (242, 255, 255)),
        "kind": "fleet",
    },
    "quantum-replication": {
        "title": "Quantum Replication",
        "palette": ((190, 100, 255), (109, 228, 255), (255, 239, 255)),
        "kind": "replicator",
    },
    "antimatter-containment": {
        "title": "Antimatter Containment",
        "palette": ((206, 100, 255), (109, 228, 255), (255, 255, 255)),
        "kind": "capsule",
    },
    "interstellar-xenobiology": {
        "title": "Interstellar Xenobiology",
        "palette": ((94, 235, 128), (255, 205, 66), (221, 255, 190)),
        "kind": "biochamber",
    },
    "quantum-fabrication": {
        "title": "Quantum Fabrication",
        "palette": ((190, 100, 255), (255, 218, 108), (255, 239, 255)),
        "kind": "fabricator",
    },
    "orbital-industry": {
        "title": "Orbital Industry",
        "palette": ((255, 146, 72), (106, 190, 255), (255, 239, 202)),
        "kind": "foundry",
    },
    "interstellar-dust-crushing": {
        "title": "Interstellar Dust Crushing",
        "palette": ((255, 205, 66), (146, 150, 158), (255, 255, 190)),
        "kind": "crusher",
    },
    "deep-dust-prospecting": {
        "title": "Deep Dust Prospecting",
        "palette": ((255, 205, 66), (206, 100, 255), (255, 255, 190)),
        "kind": "crusher",
    },
    "stellar-fusion-drive-efficiency": {
        "title": "Fusion Drive Efficiency",
        "palette": ((86, 210, 255), (55, 82, 130), (235, 255, 255)),
        "kind": "drive",
    },
    "antimatter-drive-efficiency": {
        "title": "Antimatter Drive Efficiency",
        "palette": ((210, 96, 255), (75, 52, 118), (255, 236, 255)),
        "kind": "drive",
    },
    "interstellar-dust-collection-productivity": {
        "title": "Dust Collection Productivity",
        "palette": ((255, 205, 66), (98, 110, 126), (255, 255, 190)),
        "kind": "collector",
    },
    "quantum-replication-productivity": {
        "title": "Quantum Replication Productivity",
        "palette": ((190, 100, 255), (109, 228, 255), (255, 239, 255)),
        "kind": "replicator",
    },
    "fleet-coordination": {
        "title": "Fleet Coordination",
        "palette": ((106, 190, 255), (255, 218, 108), (205, 225, 245)),
        "kind": "fleet",
    },
}

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

ITEM_ICON_NAMES = [
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


def alpha_composite(base: Image.Image, overlay: Image.Image) -> None:
    base.alpha_composite(overlay)


def glow(size: int, color: tuple[int, int, int], radius: float, intensity: int = 150) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    center = size // 2
    draw.ellipse(
        (center - radius, center - radius, center + radius, center + radius),
        fill=(*color, intensity),
    )
    return image.filter(ImageFilter.GaussianBlur(radius / 2.5))


def polygon_points(cx: float, cy: float, radius: float, sides: int, rotation: float) -> list[tuple[float, float]]:
    return [
        (
            cx + math.cos(rotation + i * math.tau / sides) * radius,
            cy + math.sin(rotation + i * math.tau / sides) * radius,
        )
        for i in range(sides)
    ]


def draw_machine(draw: ImageDraw.ImageDraw, size: int, palette, kind: str, frame: int) -> None:
    primary, secondary, highlight = palette
    pulse = frame / 4
    cx = cy = size / 2
    shadow = (0, 0, 0, 90)
    outline = (18, 23, 30, 230)
    metal = tuple(int(secondary[i] * 0.85) for i in range(3))

    draw.ellipse((size * 0.18, size * 0.76, size * 0.82, size * 0.93), fill=shadow)

    if kind in {"orb", "capsule"}:
        draw.ellipse((size * 0.2, size * 0.2, size * 0.8, size * 0.8), fill=outline)
        draw.ellipse((size * 0.26, size * 0.26, size * 0.74, size * 0.74), fill=primary)
        draw.arc((size * 0.14, size * 0.33, size * 0.86, size * 0.67), 10 + frame * 18, 350 + frame * 18, fill=highlight, width=max(2, size // 18))
        draw.ellipse((size * 0.38, size * 0.32, size * 0.5, size * 0.44), fill=highlight)
        return

    if kind == "crate":
        draw.rounded_rectangle((size * 0.22, size * 0.32, size * 0.78, size * 0.74), radius=size * 0.08, fill=outline)
        draw.rounded_rectangle((size * 0.27, size * 0.27, size * 0.73, size * 0.69), radius=size * 0.07, fill=secondary)
        draw.line((size * 0.31, size * 0.47, size * 0.69, size * 0.47), fill=primary, width=max(2, size // 14))
        draw.polygon(polygon_points(cx, cy, size * 0.14, 6, pulse * math.tau), fill=highlight)
        return

    if kind in {"drive"}:
        draw.polygon([(size * 0.28, size * 0.22), (size * 0.72, size * 0.38), (size * 0.72, size * 0.68), (size * 0.28, size * 0.82)], fill=outline)
        draw.polygon([(size * 0.34, size * 0.29), (size * 0.67, size * 0.42), (size * 0.67, size * 0.64), (size * 0.34, size * 0.75)], fill=metal)
        flame = 0.18 + 0.04 * math.sin(frame * math.tau / 4)
        draw.polygon([(size * 0.19, size * 0.43), (size * (0.19 - flame), size * 0.52), (size * 0.19, size * 0.61)], fill=primary)
        draw.polygon([(size * 0.24, size * 0.48), (size * (0.24 - flame * 0.55), size * 0.52), (size * 0.24, size * 0.57)], fill=highlight)
        draw.ellipse((size * 0.58, size * 0.45, size * 0.78, size * 0.63), fill=primary)
        return

    draw.rounded_rectangle((size * 0.2, size * 0.3, size * 0.8, size * 0.78), radius=size * 0.08, fill=outline)
    draw.rounded_rectangle((size * 0.26, size * 0.26, size * 0.74, size * 0.72), radius=size * 0.06, fill=metal)
    draw.rectangle((size * 0.32, size * 0.66, size * 0.68, size * 0.8), fill=outline)

    if kind in {"lab", "replicator", "fabricator"}:
        draw.polygon(polygon_points(cx, cy, size * 0.21, 6, pulse * math.tau), fill=outline)
        draw.polygon(polygon_points(cx, cy, size * 0.16, 6, pulse * math.tau), fill=primary)
        draw.polygon(polygon_points(cx, cy, size * 0.08, 6, -pulse * math.tau), fill=highlight)
    elif kind == "collector":
        for i in range(4):
            angle = pulse * math.tau + i * math.tau / 4
            x = cx + math.cos(angle) * size * 0.22
            y = cy + math.sin(angle) * size * 0.22
            draw.line((cx, cy, x, y), fill=primary, width=max(2, size // 24))
            draw.ellipse((x - size * 0.05, y - size * 0.05, x + size * 0.05, y + size * 0.05), fill=highlight)
        draw.ellipse((size * 0.43, size * 0.43, size * 0.57, size * 0.57), fill=primary)
    elif kind in {"foundry", "crusher"}:
        fill = tuple(min(255, int(primary[i] * (0.7 + 0.25 * math.sin(frame * math.tau / 4)))) for i in range(3))
        draw.polygon([(size * 0.35, size * 0.34), (size * 0.65, size * 0.34), (size * 0.58, size * 0.62), (size * 0.42, size * 0.62)], fill=fill)
        draw.line((size * 0.32, size * 0.36, size * 0.68, size * 0.36), fill=highlight, width=max(2, size // 20))
    elif kind == "electromagnetic":
        for i in range(3):
            offset = (i - 1) * size * 0.12
            draw.arc((size * 0.32 + offset, size * 0.36, size * 0.62 + offset, size * 0.66), 70, 290, fill=primary, width=max(2, size // 20))
        draw.line((size * 0.35, size * 0.51, size * 0.65, size * 0.51), fill=highlight, width=max(2, size // 22))
    elif kind == "biochamber":
        draw.ellipse((size * 0.34, size * 0.33, size * 0.66, size * 0.65), fill=primary)
        draw.arc((size * 0.38, size * 0.38, size * 0.62, size * 0.62), frame * 35, 250 + frame * 35, fill=highlight, width=max(2, size // 20))
    elif kind == "cryogenic":
        draw.polygon(polygon_points(cx, cy, size * 0.18, 6, math.pi / 6), outline=highlight, fill=primary)
        draw.line((cx, size * 0.32, cx, size * 0.66), fill=highlight, width=max(2, size // 22))
        draw.line((size * 0.35, cy, size * 0.65, cy), fill=highlight, width=max(2, size // 22))
    elif kind == "fleet":
        for i in range(3):
            x = size * (0.36 + i * 0.11)
            y = size * (0.44 + i * 0.06)
            draw.polygon([(x, y - size * 0.12), (x + size * 0.18, y), (x, y + size * 0.12)], fill=primary if i == 1 else secondary)


def make_frame(name: str, size: int, frame: int) -> Image.Image:
    spec = ASSETS[name]
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    primary = spec["palette"][0]
    alpha_composite(image, glow(size, primary, size * (0.22 + 0.03 * math.sin(frame * math.tau / 4))))
    draw = ImageDraw.Draw(image)
    draw_machine(draw, size, spec["palette"], spec["kind"], frame)
    return image


def make_icon(name: str, destination: Path, size: int = 64) -> None:
    image = make_frame(name, size, 1)
    image = ImageEnhance.Sharpness(image).enhance(1.3)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)


def make_tech(name: str, destination: Path) -> None:
    size = 128
    image = Image.new("RGBA", (size, size), (12, 16, 22, 255))
    primary, secondary, highlight = ASSETS[name]["palette"]
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, size, size), fill=(13, 18, 27, 255))
    for i in range(12):
        x = (i * 37) % size
        y = (i * 53) % size
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(*highlight, 120))
    alpha_composite(image, glow(size, primary, 42, 130))
    icon = make_frame(name, 96, 2)
    image.alpha_composite(icon, (16, 14))
    draw.rounded_rectangle((4, 4, size - 5, size - 5), radius=14, outline=(*secondary, 230), width=3)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)


def make_entity_assets(name: str) -> None:
    directory = ENTITY / name
    directory.mkdir(parents=True, exist_ok=True)
    frames = [make_frame(name, 128, frame) for frame in range(4)]
    sheet = Image.new("RGBA", (128 * 4, 128), (0, 0, 0, 0))
    glow_sheet = Image.new("RGBA", (128 * 4, 128), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, (index * 128, 0))
        primary = ASSETS[name]["palette"][0]
        glow_frame = glow(128, primary, 28 + 4 * math.sin(index * math.tau / 4), 170)
        glow_sheet.alpha_composite(glow_frame, (index * 128, 0))
    sheet.save(directory / f"{name}-animation.png")
    glow_sheet.save(directory / f"{name}-glow.png")
    frames[0].save(
        PREVIEWS / f"{name}.gif",
        save_all=True,
        append_images=frames[1:],
        duration=140,
        loop=0,
        disposal=2,
    )


def make_preview_sheet() -> None:
    names = ITEM_ICON_NAMES
    cell = 96
    cols = 4
    rows = math.ceil(len(names) / cols)
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (16, 20, 24, 255))
    draw = ImageDraw.Draw(sheet)
    for index, name in enumerate(names):
        x = (index % cols) * cell
        y = (index // cols) * cell
        draw.rectangle((x, y, x + cell - 1, y + cell - 1), outline=(49, 65, 80, 255))
        icon = Image.open(ICONS / f"{name}.png").convert("RGBA")
        sheet.alpha_composite(icon, (x + 16, y + 8))
        draw.text((x + 6, y + 76), name.replace("interstellar-", "i-")[:16], fill=(215, 221, 229, 255))
    sheet.save(ROOT / "graphics" / "art-preview-sheet.png")


def main() -> None:
    for directory in [ICONS, TECH, ENTITY, PREVIEWS]:
        directory.mkdir(parents=True, exist_ok=True)
    for name in ITEM_ICON_NAMES:
        make_icon(name, ICONS / f"{name}.png")
    for name in TECH_NAMES:
        make_tech(name, TECH / f"{name}.png")
    for name in ENTITY_NAMES:
        make_entity_assets(name)
    make_preview_sheet()


if __name__ == "__main__":
    main()
