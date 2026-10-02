"""Pack fixed-origin Blender passes and compose the complete art review collection.

Python 3.10+ / Pillow 11.3.0. No downloaded artwork, fonts, or input photographs.
Run after blender_render_assets.py. All paths in the release manifest are relative.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import random
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageMath

ROOT = Path(__file__).resolve().parents[1]
RENDERS = ROOT / "tmp" / "blender-renders"
ENTITY_NAMES = [
    "interstellar-lab", "quantum-replicator", "interstellar-dust-collector",
    "stellar-fusion-drive", "antimatter-drive", "interstellar-foundry",
    "interstellar-electromagnetic-plant", "interstellar-biochamber",
    "interstellar-cryogenic-plant",
]
ITEM_NAMES = ["interstellar-dust", "antimatter", "ship-starter-pack"]
MODEL_NAMES = ENTITY_NAMES + ITEM_NAMES
TITLES = {name: name.replace("-", " ").capitalize() for name in MODEL_NAMES}
LABELS = {
    "interstellar-lab": ("SCIENCE / RESEARCH", "A new horizon for industrial science", (101, 209, 216)),
    "quantum-replicator": ("MATTER / FABRICATION", "Precision machinery for impossible materials", (172, 142, 229)),
    "interstellar-dust-collector": ("ORBIT / EXTRACTION", "Every fragment becomes a resource", (218, 173, 90)),
    "stellar-fusion-drive": ("PROPULSION / FUSION", "Sustained thrust for the long journey", (112, 194, 221)),
    "antimatter-drive": ("PROPULSION / ANTIMATTER", "Extreme energy, industrial containment", (191, 130, 216)),
    "interstellar-foundry": ("INDUSTRY / METALLURGY", "Heavy metalworking beyond the planetary frontier", (231, 148, 86)),
    "interstellar-electromagnetic-plant": ("INDUSTRY / ELECTROMAGNETICS", "High-energy manufacture in a compact envelope", (108, 197, 198)),
    "interstellar-biochamber": ("INDUSTRY / XENOBIOLOGY", "Life-support engineering for alien processes", (153, 193, 105)),
    "interstellar-cryogenic-plant": ("INDUSTRY / CRYOGENICS", "Thermal control at the edge of absolute zero", (151, 205, 229)),
    "interstellar-dust": ("RESOURCE / INTERSTELLAR", "Recovered matter from the space between stars", (222, 183, 108)),
    "antimatter": ("RESOURCE / CONTAINMENT", "A captured energy source for advanced industry", (193, 140, 225)),
    "ship-starter-pack": ("FLEET / CONSTRUCTION", "The foundation of the next expedition", (170, 194, 212)),
}
# Source arrangements and glyphs are deliberately different, including upgrades.
TECH_SPECS = {
    "interstellar-fleets": (["ship-starter-pack", "interstellar-lab"], "orbit"),
    "quantum-replication": (["quantum-replicator"], "duplicate"),
    "antimatter-containment": (["antimatter"], "shield"),
    "interstellar-xenobiology": (["interstellar-biochamber"], "helix"),
    "quantum-fabrication": (["interstellar-electromagnetic-plant", "quantum-replicator"], "chip"),
    "orbital-industry": (["interstellar-foundry", "interstellar-cryogenic-plant"], "factory"),
    "fleet-printing": (["ship-starter-pack", "quantum-replicator"], "plus"),
    "interstellar-dust-crushing": (["interstellar-dust"], "crush"),
    "deep-dust-prospecting": (["interstellar-dust-collector", "interstellar-dust"], "scan"),
    "stellar-fusion-drive-efficiency": (["stellar-fusion-drive"], "energy"),
    "antimatter-drive-efficiency": (["antimatter-drive"], "double-energy"),
    "interstellar-dust-collection-productivity": (["interstellar-dust-collector"], "bars"),
    "quantum-replication-productivity": (["quantum-replicator", "antimatter"], "rising"),
    "fleet-coordination": (["ship-starter-pack"], "network"),
}
PAPER = (227, 230, 219)
MUTED = (129, 146, 148)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int) -> ImageFont.FreeTypeFont:
    # Pillow's embedded Aileron font makes boards portable and self-contained.
    return ImageFont.load_default(size=size)


def text(draw: ImageDraw.ImageDraw, xy, value: str, size: int, color=PAPER, **kwargs) -> None:
    draw.text(xy, value, font=font(size), fill=color, **kwargs)


def open_rgba(path: Path) -> Image.Image:
    with Image.open(path) as source:
        return source.convert("RGBA")


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def tight(image: Image.Image) -> Image.Image:
    bounds = image.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("Cannot compose an empty render")
    return image.crop(bounds)


def fit(image: Image.Image, box: tuple[int, int], *, crop: bool = True) -> Image.Image:
    image = tight(image) if crop else image.copy()
    image.thumbnail(box, Image.Resampling.LANCZOS)
    return image


def place(canvas: Image.Image, source: Image.Image, box, *, crop: bool = True) -> None:
    x0, y0, x1, y1 = box
    scaled = fit(source, (int(x1 - x0), int(y1 - y0)), crop=crop)
    canvas.alpha_composite(scaled, (int((x0 + x1 - scaled.width) / 2), int((y0 + y1 - scaled.height) / 2)))


def panel_background(size: tuple[int, int], accent, *, grid: bool = True) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        amount = 1 - abs(y / height - 0.43)
        color = tuple(int(a + b * amount) for a, b in ((13, 10), (18, 13), (20, 14)))
        draw.line((0, y, width, y), fill=(*color, 255))
    if grid:
        spacing = max(24, width // 20)
        for x in range(0, width, spacing):
            draw.line((x, 0, x, height), fill=(38, 49, 51), width=1)
        for y in range(0, height, spacing):
            draw.line((0, y, width, y), fill=(34, 44, 46), width=1)
    haze = Image.new("RGBA", size)
    hazedraw = ImageDraw.Draw(haze)
    hazedraw.ellipse((width * .12, height * .1, width * .88, height * .82), fill=(*accent, 15))
    image.alpha_composite(haze.filter(ImageFilter.GaussianBlur(max(16, width // 10))))
    return image


def corner_marks(draw: ImageDraw.ImageDraw, bounds, color, length: int = 20) -> None:
    x0, y0, x1, y1 = bounds
    for x, dx in ((x0, length), (x1, -length)):
        for y, dy in ((y0, length), (y1, -length)):
            draw.line((x, y + dy, x, y, x + dx, y), fill=color, width=2)


def load_metadata(name: str) -> dict:
    metadata = json.loads((RENDERS / name / "metadata.json").read_text())
    if name in ENTITY_NAMES:
        for key in ("width", "height", "frame_count", "line_length", "directions", "scale", "shift"):
            if key not in metadata:
                raise ValueError(f"{name}: metadata missing {key}")
        if metadata["line_length"] != metadata["frame_count"]:
            raise ValueError(f"{name}: packer requires one complete cycle per direction row")
    return metadata


def frame_path(name: str, direction: int, index: int, layer: str) -> Path:
    prefix = {"animation": "frame", "glow": "glow", "shadow": "shadow"}[layer]
    directory = RENDERS / name / f"direction_{direction}"
    # Accept both the renderer's plain integers and zero-padded export names.
    for filename in (f"{prefix}_{index}.png", f"{prefix}_{index:02d}.png"):
        path = directory / filename
        if path.exists():
            return path
    raise FileNotFoundError(directory / f"{prefix}_{index}.png")


def additive(canvas: Image.Image, glow: Image.Image) -> Image.Image:
    emission = Image.new("RGBA", glow.size, (0, 0, 0, 255))
    emission.alpha_composite(glow)
    result = ImageChops.add(canvas.convert("RGB"), emission.convert("RGB"))
    return result.convert("RGBA")


def prepare_pass(frame: Image.Image, layer: str) -> Image.Image:
    if layer == "glow":
        # Blender's emission-only scene keeps black occluders. Make them fully
        # transparent and unpremultiply color to preserve RGB * alpha exactly.
        r, g, b, original_alpha = frame.split()
        intensity = ImageChops.lighter(ImageChops.lighter(r, g), b)
        divisor = intensity.point(lambda value: max(1, value))
        channels = [ImageMath.lambda_eval(
            lambda args: args["convert"](args["channel"] * 255 / args["divisor"], "L"),
            channel=channel, divisor=divisor) for channel in (r, g, b)]
        return Image.merge("RGBA", (*channels, ImageChops.multiply(original_alpha, intensity)))
    if layer == "shadow":
        frame = frame.copy()
        frame.putalpha(frame.getchannel("A").point(lambda value: round(value * .32)))
    return frame


def pack_entity(name: str, metadata: dict) -> dict:
    width, height = metadata["width"], metadata["height"]
    count, columns, directions = metadata["frame_count"], metadata["line_length"], metadata["directions"]
    result = {key: metadata[key] for key in ("width", "height", "frame_count", "line_length", "directions", "scale", "shift")}
    result["animation_speed"] = .15
    if "flame_position" in metadata:
        result["flame_position"] = metadata["flame_position"]
    result["sha256"] = {}
    first_direction = {}
    for layer in ("animation", "glow", "shadow"):
        sheet = Image.new("RGBA", (width * columns, height * directions))
        frames = []
        for direction in range(directions):
            for index in range(count):
                frame = open_rgba(frame_path(name, direction, index, layer))
                if frame.size != (width, height):
                    raise ValueError(f"{name} {layer} {direction}/{index}: unexpected size {frame.size}")
                frame = prepare_pass(frame, layer)
                # Paste intact cells. Pass-specific alpha conversion is pixelwise;
                # never rescale, recenter, crop, or fabricate a silhouette glow.
                sheet.paste(frame, (index * width, direction * height))
                if direction == 0:
                    frames.append(frame)
        first_direction[layer] = frames
        path = ROOT / "graphics" / "entity" / name / f"{name}-{layer}.png"
        save(sheet, path)
        result[layer] = relative(path)
        result["sha256"][layer] = digest(path)
    previews = []
    for index in range(count):
        background = panel_background((width, height), LABELS[name][2], grid=False)
        background.alpha_composite(first_direction["shadow"][index])
        background.alpha_composite(first_direction["animation"][index])
        background = additive(background, first_direction["glow"][index])
        previews.append(background.resize((256, 256), Image.Resampling.LANCZOS).convert("RGB"))
    # A single shared palette avoids color pumping between GIF frames.
    palette_source = Image.new("RGB", (256 * count, 256))
    for index, frame in enumerate(previews):
        palette_source.paste(frame, (256 * index, 0))
    palette = palette_source.quantize(colors=255)
    previews = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in previews]
    path = ROOT / "graphics" / "previews" / f"{name}.gif"
    path.parent.mkdir(parents=True, exist_ok=True)
    previews[0].save(path, save_all=True, append_images=previews[1:], duration=110, loop=0, disposal=2, optimize=False)
    result["preview"] = relative(path)
    result["sha256"]["preview"] = digest(path)
    return result


def save_icon(name: str, hero: Image.Image) -> Path:
    icon = Image.new("RGBA", (64, 64))
    place(icon, hero, (3, 3, 61, 61))
    path = ROOT / "graphics" / "icons" / f"{name}.png"
    save(icon, path)
    return path


def save_sample(name: str, hero: Image.Image, metadata: dict) -> Path:
    category, subtitle, accent = LABELS[name]
    out = panel_background((1200, 1000), accent)
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, 1199, 121), fill=(17, 24, 26))
    draw.rectangle((46, 36, 52, 91), fill=accent)
    text(draw, (72, 32), "INTERSTELLAR FLEETS", 27)
    text(draw, (73, 73), category, 16, accent)
    text(draw, (1134, 39), f"ASSET {MODEL_NAMES.index(name) + 1:02d} / 12", 16, MUTED, anchor="ra")
    text(draw, (1134, 72), "BLENDER / MODEL STUDY", 14, MUTED, anchor="ra")
    draw.line((46, 121, 1154, 121), fill=(65, 78, 78), width=1)
    corner_marks(draw, (56, 149, 1144, 818), (81, 104, 105), 23)
    # Ground contact is presentation-only; in-game shadows are Blender passes.
    shadow = Image.new("RGBA", out.size)
    ImageDraw.Draw(shadow).ellipse((210, 670, 990, 812), fill=(0, 0, 0, 125))
    out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(38)))
    place(out, hero, (140, 170, 1060, 788))
    draw = ImageDraw.Draw(out)
    text(draw, (77, 849), TITLES[name], 35 if len(TITLES[name]) < 33 else 31)
    text(draw, (79, 899), subtitle, 19, MUTED)
    draw.line((78, 944, 1122, 944), fill=(65, 78, 78))
    text(draw, (79, 963), "EDITABLE 3D SOURCE  /  ORTHOGRAPHIC RENDER  /  ORIGINAL MOD ART", 13, MUTED)
    text(draw, (1120, 963), f"{metadata.get('mesh_count', 0):03d} MESHES", 13, accent, anchor="ra")
    path = ROOT / "art" / "samples" / f"{name}.png"
    save(out, path)
    return path


def draw_glyph(draw: ImageDraw.ImageDraw, kind: str, origin, size: int, color) -> None:
    """Simple semantic emblems with generous strokes for legibility at 128px."""
    ox, oy = origin
    def p(x, y):
        return (int(ox + x * size), int(oy + y * size))
    def line(points, width=6):
        draw.line([p(*point) for point in points], fill=color, width=max(2, int(size * width / 100)), joint="curve")
    def ellipse(bounds, width=5):
        draw.ellipse((*p(bounds[0], bounds[1]), *p(bounds[2], bounds[3])), outline=color, width=max(2, int(size * width / 100)))
    if kind == "orbit":
        ellipse((.05, .3, .95, .72)); ellipse((.34, .1, .66, .9)); ellipse((.42, .42, .58, .58), 8)
    elif kind == "duplicate":
        for x, y in ((.1, .1), (.33, .34)):
            line([(x, y+.52), (x, y), (x+.52, y), (x+.52, y+.52), (x, y+.52)])
    elif kind == "shield":
        line([(.5,.07),(.88,.23),(.81,.66),(.5,.92),(.19,.66),(.12,.23),(.5,.07)])
        line([(.31,.49),(.46,.65),(.71,.36)])
    elif kind == "helix":
        for flip in (0, 1):
            line([(.5 + math.sin(i/20*math.tau) * .28 * (1 if flip else -1), .07 + i*.043) for i in range(21)])
        for y in (.25,.5,.75): line([(.3,y),(.7,y)], 4)
    elif kind == "chip":
        line([(.25,.25),(.75,.25),(.75,.75),(.25,.75),(.25,.25)])
        for t in (.35,.5,.65):
            line([(.08,t),(.25,t)]); line([(.75,t),(.92,t)]); line([(t,.08),(t,.25)]); line([(t,.75),(t,.92)])
    elif kind == "factory":
        line([(.12,.85),(.12,.42),(.37,.25),(.37,.42),(.62,.25),(.62,.42),(.8,.42),(.8,.15),(.9,.15),(.9,.85),(.12,.85)])
    elif kind == "plus":
        line([(.15,.5),(.85,.5)], 11); line([(.5,.15),(.5,.85)], 11)
    elif kind == "crush":
        line([(.08,.17),(.3,.4),(.08,.62)]); line([(.92,.17),(.7,.4),(.92,.62)])
        line([(.5,.23),(.64,.43),(.5,.65),(.36,.43),(.5,.23)]); line([(.23,.84),(.78,.84)])
    elif kind == "scan":
        ellipse((.13,.13,.7,.7)); line([(.64,.64),(.91,.91)], 9); line([(.24,.42),(.57,.42)], 4); line([(.42,.24),(.42,.57)], 4)
    elif kind in ("energy", "double-energy"):
        offsets = [-.15,.18] if kind == "double-energy" else [0]
        for x in offsets:
            line([(.55+x,.08),(.28+x,.54),(.54+x,.54),(.42+x,.92),(.77+x,.39),(.5+x,.39),(.55+x,.08)])
    elif kind == "bars":
        for x, y in ((.16,.62),(.4,.4),(.66,.16)):
            line([(x,.87),(x,y),(x+.13,y),(x+.13,.87)], 7)
    elif kind == "rising":
        line([(.13,.83),(.4,.55),(.56,.63),(.85,.18)], 8); line([(.6,.19),(.86,.17),(.88,.46)], 8)
    elif kind == "network":
        for x,y in ((.5,.17),(.2,.77),(.8,.77)):
            line([(.5,.49),(x,y)],4); ellipse((x-.11,y-.11,x+.11,y+.11),8)
        ellipse((.38,.37,.62,.61),8)


def save_tech(name: str, heroes: dict[str, Image.Image]) -> dict:
    sources, glyph = TECH_SPECS[name]
    accent = LABELS[sources[0]][2]
    out = panel_background((512, 512), accent, grid=False)
    draw = ImageDraw.Draw(out)
    draw.rounded_rectangle((14, 14, 498, 498), radius=39, outline=(104, 111, 103), width=8)
    draw.rounded_rectangle((28, 28, 484, 484), radius=29, outline=(52, 65, 67), width=3)
    for i in range(12):
        angle = i * math.tau / 12
        x,y = 256+math.cos(angle)*209,256+math.sin(angle)*209
        draw.line((x,y,256+math.cos(angle)*194,256+math.sin(angle)*194), fill=accent, width=5)
    draw.ellipse((72, 72, 440, 440), outline=(*accent, 255), width=3)
    if name == "fleet-coordination":
        for box in ((145,55,370,270),(45,195,280,415),(267,165,483,373)):
            place(out, heroes[sources[0]], box)
    elif len(sources) == 2:
        place(out, heroes[sources[1]], (193, 52, 452, 296))
        place(out, heroes[sources[0]], (43, 132, 360, 447))
    else:
        place(out, heroes[sources[0]], (47, 57, 456, 445))
    draw = ImageDraw.Draw(out)
    draw.rounded_rectangle((334, 334, 492, 492), radius=26, fill=(20, 30, 32), outline=accent, width=7)
    draw_glyph(draw, glyph, (351, 350), 123, accent)
    path = ROOT / "graphics" / "technology" / f"{name}.png"
    save(out.resize((128,128), Image.Resampling.LANCZOS), path)
    return {"path": relative(path), "source_models": sources, "glyph": glyph, "sha256": digest(path)}


def save_contact_sheet(heroes: dict[str, Image.Image]) -> Path:
    out = panel_background((1800, 1600), (151, 171, 179), grid=False)
    draw = ImageDraw.Draw(out)
    text(draw, (64, 37), "INTERSTELLAR FLEETS", 49)
    text(draw, (66, 100), "TWELVE ORIGINAL BLENDER MODELS / INDUSTRY AT THE EDGE OF SPACE", 20, MUTED)
    text(draw, (1734, 47), "ART COLLECTION 01", 20, (195, 164, 104), anchor="ra")
    for index, name in enumerate(MODEL_NAMES):
        x, y = 52 + (index % 3)*570, 161 + (index // 3)*345
        accent = LABELS[name][2]
        card = panel_background((554, 327), accent, grid=False)
        cd = ImageDraw.Draw(card)
        cd.rectangle((0,0,553,326), outline=(65, 80, 81), width=1)
        cd.line((19, 22, 65, 22), fill=accent, width=3)
        text(cd, (523, 18), f"{index+1:02d}", 16, accent, anchor="ra")
        place(card, heroes[name], (65, 31, 489, 250))
        cd = ImageDraw.Draw(card)
        text(cd, (25, 262), TITLES[name], 22 if len(TITLES[name]) < 32 else 20)
        text(cd, (26, 299), LABELS[name][0], 12, accent)
        out.alpha_composite(card, (x, y))
    draw = ImageDraw.Draw(out)
    text(draw, (65, 1571), "9 ANIMATED MACHINES  /  3 INVENTORY MODELS  /  14 RESEARCH EMBLEMS  /  FIXED-ORIGIN SPRITE ATLASES", 16, MUTED)
    path = ROOT / "graphics" / "art-preview-sheet.png"
    save(out, path)
    return path


def space_background(size: tuple[int, int]) -> Image.Image:
    width, height = size
    rng = random.Random(29017)
    out = Image.new("RGBA", size, (9, 15, 23, 255))
    cloud = Image.new("RGBA", size)
    cd = ImageDraw.Draw(cloud)
    for _ in range(32):
        x = rng.randrange(-width//3, width)
        y = int(height*.68 - x*.24 + rng.randrange(-100, 100))
        radius = rng.randrange(90, 310)
        cd.ellipse((x-radius,y-radius//2,x+radius,y+radius//2),fill=rng.choice([(67,97,117,32),(91,57,51,32),(132,105,63,27)]))
    out.alpha_composite(cloud.filter(ImageFilter.GaussianBlur(max(25,width//35))))
    draw = ImageDraw.Draw(out)
    for _ in range(int(width*height/1800)):
        x, y = rng.randrange(width),rng.randrange(height)
        bright = rng.randrange(60,175)
        draw.point((x,y),fill=(bright,bright,min(255,bright+15)))
    for _ in range(max(3,width//90)):
        x, y = rng.randrange(width),rng.randrange(height)
        draw.line((x-2,y,x+2,y),fill=(150,167,178)); draw.line((x,y-2,x,y+2),fill=(150,167,178))
    return out


def save_key_art(heroes: dict[str, Image.Image]) -> tuple[Path, Path]:
    out = space_background((1600, 1000))
    draw = ImageDraw.Draw(out)
    draw.arc((570, 102, 1730, 1006), 200, 350, fill=(48, 69, 80), width=2)
    draw.arc((590, 125, 1700, 975), 205, 353, fill=(53, 67, 71), width=1)
    for box in ((1050,48,1348,300),(1290,266,1540,483),(1113,740,1402,965)):
        place(out, heroes["ship-starter-pack"], box)
    place(out, heroes["ship-starter-pack"], (603, 210, 1483, 851))
    # A dark scrim makes the typography robust against the procedural nebula.
    scrim = Image.new("RGBA", out.size)
    sd = ImageDraw.Draw(scrim)
    for x in range(680):
        sd.line((x,0,x,1000),fill=(8,14,19,int(225*(1-x/680))))
    out.alpha_composite(scrim)
    draw = ImageDraw.Draw(out)
    text(draw, (77, 82), "BEYOND THE SOLAR EDGE", 24, (205, 172, 115))
    text(draw, (74, 143), "INTERSTELLAR", 66)
    text(draw, (71, 215), "FLEETS", 111)
    draw.line((80, 359, 547, 359), fill=(113, 137, 139), width=2)
    text(draw, (80, 391), "AN INDUSTRIAL EXPANSION", 24, (174, 194, 197))
    text(draw, (80, 432), "Forge the fleet. Cross the dark.", 24, MUTED)
    text(draw, (80, 470), "Build what comes next.", 24, MUTED)
    for index, name in enumerate(("interstellar-lab","stellar-fusion-drive","interstellar-dust-collector")):
        x = 80 + index*165
        draw.rounded_rectangle((x,657,x+151,844),radius=8,fill=(16,27,33),outline=(57,73,79))
        place(out, heroes[name], (x+7,674,x+143,796))
        draw = ImageDraw.Draw(out)
        text(draw,(x+75,815),("RESEARCH","PROPULSION","RESOURCES")[index],11,LABELS[name][2],anchor="ma")
    text(draw, (82, 930), "ORIGINAL 3D ART COLLECTION  /  INTERSTELLAR FLEETS MOD", 17, MUTED)
    text(draw, (1520, 930), "MODEL-TO-SPRITE / 01", 17, MUTED, anchor="ra")
    path = ROOT / "art" / "samples" / "fleet-key-art.png"
    save(out, path)
    thumbnail = space_background((576,576))
    place(thumbnail, heroes["ship-starter-pack"], (46, 29, 554, 462))
    td = ImageDraw.Draw(thumbnail)
    td.rectangle((0,467,576,576),fill=(14,23,28))
    td.line((30,468,546,468),fill=(192,155,94),width=6)
    text(td,(288,486),"INTERSTELLAR",34,PAPER,anchor="ma")
    text(td,(288,530),"FLEETS",29,(175,194,198),anchor="ma")
    thumbpath = ROOT / "thumbnail.png"
    save(thumbnail.resize((144,144),Image.Resampling.LANCZOS),thumbpath)
    return path, thumbpath


def lua_value(value) -> str:
    if isinstance(value, list):
        return "{" + ", ".join(lua_value(part) for part in value) + "}"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value)
    return repr(value)


def save_lua_manifest(entities: dict) -> None:
    lines = ["-- Generated by scripts/pack_blender_assets.py. Do not edit by hand.",
             "-- All frames and passes share the Blender camera origin; shift is in tiles.", "return {"]
    for name, entity in entities.items():
        lines.append(f"  [{json.dumps(name)}] = {{")
        for key in ("width","height","frame_count","line_length","directions","scale","shift","animation_speed","flame_position"):
            if key in entity:
                lines.append(f"    {key} = {lua_value(entity[key])},")
        lines.append("  },")
    lines.append("}\n")
    (ROOT / "prototypes" / "art-manifest.lua").write_text("\n".join(lines))


def save_gallery() -> None:
    cards = []
    for name in MODEL_NAMES:
        preview = f'<img class="motion" loading="lazy" src="../graphics/previews/{name}.gif" alt="{html.escape(TITLES[name])} eight-frame animation">' if name in ENTITY_NAMES else ""
        cards.append(f'''<article class="asset"><a href="../art/samples/{name}.png"><img class="sample" loading="lazy" src="../art/samples/{name}.png" alt="{html.escape(TITLES[name])} model presentation"></a><div class="asset-body">{preview}<div><p class="eyebrow">{LABELS[name][0]}</p><h3>{html.escape(TITLES[name])}</h3><p>{LABELS[name][1]}.</p><p class="links"><a href="../art/models/{name}.blend">Blender source</a><a href="../art/renders/{name}.png">Transparent render</a><a href="../graphics/icons/{name}.png">64px icon</a></p></div></div></article>''')
    technologies = []
    for name, (sources, glyph) in TECH_SPECS.items():
        technologies.append(f'<figure><a href="../graphics/technology/{name}.png"><img loading="lazy" src="../graphics/technology/{name}.png" alt="{name.replace("-", " ")}"></a><figcaption>{name.replace("-", " ").capitalize()}</figcaption></figure>')
    template = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Art collection | Interstellar Fleets</title>
<style>
:root{color-scheme:dark;--bg:#0c1318;--panel:#162229;--line:#34474c;--muted:#9aadb0;--ink:#e2e7df;--accent:#cbb07b}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}a{color:#b9d9db;text-underline-offset:4px}a:hover{color:#fff}header,main,footer{max-width:1500px;margin:auto;padding:28px 40px}header{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}header a{font-size:14px}header strong{letter-spacing:.16em;font-size:14px}main{padding-top:34px}h1{font-size:clamp(34px,5vw,68px);line-height:1.12;letter-spacing:-.04em;margin:18px 0}h2{font-size:30px;margin:54px 0 12px}h3{font-size:20px;line-height:1.3;margin:5px 0 10px}p{max-width:820px;color:var(--muted)}.eyebrow{font-size:11px;letter-spacing:.14em;color:var(--accent);margin:0}.hero{display:block;width:100%;border:1px solid var(--line);border-radius:12px;margin:30px 0}.summary{display:flex;gap:12px;flex-wrap:wrap}.summary span{border:1px solid var(--line);padding:7px 13px;border-radius:5px;color:var(--muted);font-size:13px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;margin-top:26px}.asset{border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--panel)}.sample{display:block;width:100%;height:auto}.asset-body{padding:22px;display:flex;gap:18px}.asset-body p{font-size:13px;margin:8px 0}.motion{height:112px;width:112px;flex:none;border-radius:6px;background:#101c23}.links{display:flex;flex-wrap:wrap;gap:13px}.links a{font-size:12px}.tech-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:14px}.tech-grid figure{padding:20px 10px;margin:0;text-align:center;background:var(--panel);border:1px solid var(--line);border-radius:7px}.tech-grid img{width:100%;max-width:128px;aspect-ratio:1}.tech-grid figcaption{font-size:12px;line-height:1.35;margin-top:12px;color:var(--muted)}.delivery{display:flex;align-items:center;gap:30px;background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:28px}.delivery img{width:144px;height:144px;flex:none}.contact{width:100%;display:block;border:1px solid var(--line);border-radius:8px}footer{margin-top:46px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}@media(max-width:900px){.tech-grid{grid-template-columns:repeat(4,minmax(0,1fr))}.grid{grid-template-columns:1fr}}@media(max-width:520px){header,main,footer{padding-left:18px;padding-right:18px}.tech-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.asset-body{display:block}.motion{float:right;margin:0 0 10px 12px;width:90px;height:90px}.delivery{display:block}.summary{gap:6px}}
</style></head><body><header><strong>INTERSTELLAR FLEETS</strong><a href="index.html">Mod wiki</a></header><main>
<p class="eyebrow">ORIGINAL BLENDER ART / COLLECTION 01</p><h1>Industry beyond<br>the solar edge.</h1><p>A complete, editable model-to-sprite art collection. Heavy fabricated metals, practical machinery, restrained energy accents, and a shared orthographic camera bring the fleet's research, resources, and industry into one visual family.</p>
<div class="summary"><span>12 editable 3D models</span><span>9 animated machines</span><span>14 research emblems</span><span>3 render passes per machine</span></div>
<a href="../art/samples/fleet-key-art.png"><img class="hero" src="../art/samples/fleet-key-art.png" alt="Interstellar Fleets poster featuring the original 3D fleet model in deep space"></a>
<h2>The complete collection</h2><p>Each sample comes from its matching Blender model. Machine animations below use the same fixed-origin body, emission, and shadow frames packed into the game atlases.</p><div class="grid">__CARDS__</div>
<h2>Research emblems</h2><p>Fourteen distinct compositions, derived from the same rendered models. Semantic emblems distinguish discovery, fabrication, containment, efficiency, and productivity at inventory scale.</p><div class="tech-grid">__TECHNOLOGIES__</div>
<h2>At a glance</h2><a href="../graphics/art-preview-sheet.png"><img class="contact" loading="lazy" src="../graphics/art-preview-sheet.png" alt="Labeled contact sheet of all twelve Blender model assets"></a>
<h2>Built to ship. Kept editable.</h2><div class="delivery"><a href="../thumbnail.png"><img src="../thumbnail.png" alt="Mod thumbnail derived from the fleet Blender model"></a><div><p>Body sprites, isolated emission, and directional ground shadows share a fixed render origin. Icons and technology art are derived from the model heroes. Source scenes, sample boards, and file checksums are included for future iteration.</p><p class="links"><a href="../docs/ART.md">Art direction &amp; reproduction guide</a><a href="../art/manifest.json">Asset manifest</a><a href="../art/render-manifest.json">Render specification</a><a href="../thumbnail.png">144px mod thumbnail</a></p></div></div>
</main><footer>Original unofficial mod artwork inspired by the industrial visual language of Factorio: Space Age. Factorio is a trademark of Wube Software. Preview loops show only the custom machine art; the game also supplies native collector arms and fluid connectors.</footer></body></html>
'''
    (ROOT / "wiki" / "art-review.html").write_text(template.replace("__CARDS__", "\n".join(cards)).replace("__TECHNOLOGIES__", "\n".join(technologies)))


def main() -> None:
    global RENDERS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renders", type=Path, default=RENDERS, help="Directory containing the completed Blender exports")
    args = parser.parse_args()
    RENDERS = args.renders.resolve()
    # Fail on missing inputs before modifying the delivered collection.
    metadata = {name: load_metadata(name) for name in MODEL_NAMES}
    heroes = {name: open_rgba(RENDERS / name / "hero.png") for name in MODEL_NAMES}
    for name in MODEL_NAMES:
        blend = ROOT / "art" / "models" / f"{name}.blend"
        if not blend.is_file():
            raise FileNotFoundError(blend)
        if name in ENTITY_NAMES:
            for direction in range(metadata[name]["directions"]):
                for index in range(metadata[name]["frame_count"]):
                    for layer in ("animation", "glow", "shadow"):
                        frame_path(name, direction, index, layer)
    manifest = {"schema_version": 2, "collection": "Interstellar Fleets / original Blender art", "generator": "scripts/pack_blender_assets.py", "render_specification": "art/render-manifest.json", "provenance": {}, "models": {}, "entities": {}, "technologies": {}, "presentation": {}}
    for key, filename in (("renderer", "scripts/blender_render_assets.py"), ("packer", "scripts/pack_blender_assets.py"), ("render_specification", "art/render-manifest.json")):
        manifest["provenance"][key] = {"path": filename, "sha256": digest(ROOT / filename)}
    for name in MODEL_NAMES:
        blend = ROOT / "art" / "models" / f"{name}.blend"
        hero_path = ROOT / "art" / "renders" / f"{name}.png"
        hero_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RENDERS / name / "hero.png", hero_path)
        icon = save_icon(name, heroes[name])
        sample = save_sample(name, heroes[name], metadata[name])
        files = {"blend": blend,"hero": hero_path,"sample": sample,"icon": icon}
        model = {key: relative(path) for key,path in files.items()}
        model.update(category="entity" if name in ENTITY_NAMES else "item", mesh_count=metadata[name].get("mesh_count",0), sha256={key:digest(path) for key,path in files.items()})
        manifest["models"][name] = model
        if name in ENTITY_NAMES:
            manifest["entities"][name] = pack_entity(name, metadata[name])
        print(f"Packed {name}")
    for name in TECH_SPECS:
        manifest["technologies"][name] = save_tech(name, heroes)
    contact = save_contact_sheet(heroes)
    key_art, thumbnail = save_key_art(heroes)
    for key, path in (("contact_sheet",contact),("key_art",key_art),("thumbnail",thumbnail)):
        with Image.open(path) as source:
            width,height = source.size
        manifest["presentation"][key] = {"path":relative(path),"width":width,"height":height,"sha256":digest(path)}
    save_lua_manifest(manifest["entities"])
    save_gallery()
    (ROOT / "art" / "manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("Packed 12 models, 27 atlases, 12 icons, 14 technology emblems, 9 animation previews, and the complete review gallery")


if __name__ == "__main__":
    main()
