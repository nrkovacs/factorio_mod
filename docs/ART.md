# Interstellar Fleets art collection

![The complete original Blender model collection](../graphics/art-preview-sheet.png)

This collection gives the mod a consistent industrial identity: dense machinery,
beveled cast-metal housings, copper and brass service hardware, ceramic insulation,
exposed pipes, and small functional pools of colored light. The forms and materials
take their visual cues from Factorio: Space Age; the models and rendered images are
original work for this mod.

Open [the art review gallery](../wiki/art-review.html) for every model, its sample
image, animated preview, transparent render, inventory icon, and editable Blender
source. [Fleet key art](../art/samples/fleet-key-art.png) and the
[mod thumbnail](../thumbnail.png) are assembled from the same model library.

Official visual and production references:

- [Friday Facts #146: The GFX workflow](https://www.factorio.com/blog/post/fff-146)
  describes editable Blender models, separate render layers, Python sprite-sheet
  packing, and animated review images.
- [Friday Facts #387: Swimming in lava](https://www.factorio.com/blog/post/fff-387)
  shows the foundry's heavy industrial forms and deliberate mechanical motion.
- [Friday Facts #399: Trash to Treasure](https://www.factorio.com/blog/post/fff-399)
  presents Fulgora's electromagnetic plant as a reference for specialized
  electrical manufacturing machinery.

## Model library

Each model has a self-contained `.blend` scene, a transparent 1024px hero render,
a labeled 1200 × 1000 sample board, and a 64px inventory icon.

| Model | Visual identity | Sample / source |
| --- | --- | --- |
| Interstellar lab | Ringed observatory, teal core, scientific instruments | [Sample](../art/samples/interstellar-lab.png) · [Blender](../art/models/interstellar-lab.blend) |
| Quantum replicator | Open magnetic portal around suspended matter | [Sample](../art/samples/quantum-replicator.png) · [Blender](../art/models/quantum-replicator.blend) |
| Interstellar dust collector | Gold parabolic intake and filtration hardware | [Sample](../art/samples/interstellar-dust-collector.png) · [Blender](../art/models/interstellar-dust-collector.blend) |
| Stellar fusion drive | Long ribbed engine with blue ceramic insulation | [Sample](../art/samples/stellar-fusion-drive.png) · [Blender](../art/models/stellar-fusion-drive.blend) |
| Antimatter drive | Violet containment hoops and a reinforced single nozzle | [Sample](../art/samples/antimatter-drive.png) · [Blender](../art/models/antimatter-drive.blend) |
| Interstellar foundry | Copper crucible, induction cage, and side chimney | [Sample](../art/samples/interstellar-foundry.png) · [Blender](../art/models/interstellar-foundry.blend) |
| Interstellar electromagnetic plant | Copper solenoid towers and service hardware | [Sample](../art/samples/interstellar-electromagnetic-plant.png) · [Blender](../art/models/interstellar-electromagnetic-plant.blend) |
| Interstellar biochamber | Three organically ribbed green culture vessels | [Sample](../art/samples/interstellar-biochamber.png) · [Blender](../art/models/interstellar-biochamber.blend) |
| Interstellar cryogenic plant | Twin insulated towers with cold process accents | [Sample](../art/samples/interstellar-cryogenic-plant.png) · [Blender](../art/models/interstellar-cryogenic-plant.blend) |
| Interstellar dust | A distinct metallic shard cluster | [Sample](../art/samples/interstellar-dust.png) · [Blender](../art/models/interstellar-dust.blend) |
| Antimatter | Guarded containment capsule | [Sample](../art/samples/antimatter.png) · [Blender](../art/models/antimatter.blend) |
| Ship starter pack | Folded industrial platform with twin engines | [Sample](../art/samples/ship-starter-pack.png) · [Blender](../art/models/ship-starter-pack.blend) |

## Production assets

The nine machines have eight-frame animation cycles with independent body,
emission, and ground-shadow passes. Each frame occupies an unchanged 512 × 512
cell. The collector has four directional rows, ordered north, east, south, west.
The other machines use one row. This produces 4096 × 512 atlases for most machines
and 4096 × 2048 atlases for the collector.

The packer copies complete frames directly into their cells. It never crops,
recenters, or resizes machine frames. The camera origin, scale, shift, and layer
registration therefore remain consistent throughout the animation. Emission
comes from the model's luminous surfaces; it is not a blurred silhouette of the
whole machine. Black emission-pass occluders become transparent; unpremultiplying
the color channels preserves their additive contribution. Shadow opacity is
reduced to 32% for in-game use. Neither operation changes any pixel's position.
The engine receives shadows through `draw_as_shadow` and emission through an
additive glow layer.

Each preview GIF is 256 × 256 and uses all eight frames from the actual sprite
passes. The same global color palette is used for every frame to prevent palette
flicker. Preview backgrounds and sample-board shadows are presentation elements,
not part of the in-game body atlas.

The collector continues to use Factorio's articulated collecting arms, and fluid
machines retain their connection overlays. Those native game effects are not
included in the custom-art GIFs. The mod's item-fueled drives use their own body
and energy animations rather than the native fluid-fueled thruster exhaust.

All twelve inventory icons are derived from their own model render. In
particular, the three resource/item icons do not reuse a machine icon. The
fourteen technology images use distinct model arrangements and semantic emblems
for containment, fabrication, fleet coordination, discovery, efficiency, and
productivity. Technology images remain 128 × 128 to match the prototypes.

## Source and provenance

| Location | Purpose |
| --- | --- |
| `art/models/*.blend` | Editable, self-contained Blender scenes |
| `art/renders/*.png` | Transparent 1024px model heroes |
| `art/samples/*.png` | Individual presentation boards and fleet poster |
| `art/render-manifest.json` | Blender render specification |
| `art/manifest.json` | Packed asset maps, dimensions, model links, SHA-256 hashes |
| `prototypes/art-manifest.lua` | Generated sprite dimensions and registration used by the mod |
| `graphics/entity/*/*.png` | Body, emission, and shadow atlases |
| `graphics/icons/*.png` | Twelve 64px model-derived icons |
| `graphics/technology/*.png` | Fourteen 128px research compositions |
| `graphics/previews/*.gif` | Nine eight-frame animated review images |
| `graphics/art-preview-sheet.png` | 1800 × 1600 labeled collection contact sheet |
| `wiki/art-review.html` | Standalone responsive review gallery |

The manifest uses schema version 2. `models` maps each model name to its `blend`,
`hero`, `sample`, and `icon` paths plus a `sha256` map for those files. `entities`
maps each machine name to the sprite metadata and its `animation`, `glow`,
`shadow`, and `preview` paths, with matching hashes. `technologies` records each
image's source model names, emblem, path, and hash. `presentation` records the
contact sheet, key art, and thumbnail with dimensions and hashes. Paths are
relative to the repository root, so a fresh clone can be checked without the
temporary render directory. `provenance` records hashes of the renderer, packer,
and render specification used to produce the collection.

The sample boards and technology emblems use Pillow's bundled Aileron font. No
system fonts, web images, stock image files, or external textures are required by
the packer. Procedural star fields use a fixed random seed. Given identical
Blender outputs and Pillow 11.3.0, packing produces identical image bytes; there
are no build timestamps in the generated manifests.

## Rebuild and verify

Use Blender 5.1 or a compatible version for the model generator, and Python 3.10+
with Pillow 11.3.0 for packing. The generator's command-line help documents its
render controls. The normal pipeline is:

```sh
blender -b --python-exit-code 1 --python scripts/blender_render_assets.py -- --asset all --samples 32
python3 scripts/pack_blender_assets.py
python3 scripts/validate_art_assets.py --blender blender
python3 scripts/build.py
```

The renderer writes complete per-model exports beneath `tmp/blender-renders/`.
Each machine has `direction_0/` (and three more directions for the collector),
containing `frame_0.png` through `frame_7.png`, corresponding `glow_*.png` and
`shadow_*.png` passes, plus model-level `hero.png` and `metadata.json`. The three
item models require their own hero and metadata. Zero-padded frame indices are
also accepted. Use `python3 scripts/pack_blender_assets.py --renders PATH` when
rendering to another directory.

To re-render a model after editing its saved Blender scene, use `--from-blend`.
Keep the `MODEL` root and its mesh, curve, and text descendants, the tagged
emissive materials, and the animation when making edits. This mode opens the
existing scene with embedded scripts disabled and renders it without saving or
overwriting the source `.blend` file. For example:

```sh
blender -b --python-exit-code 1 --python scripts/blender_render_assets.py -- --asset quantum-replicator --from-blend --samples 32
python3 scripts/pack_blender_assets.py
```

The packer then rebuilds the collection using the refreshed model exports and
the existing exports for the other models. Keep a complete set of frames in the
render directory before repacking. Without `--from-blend`, the renderer rebuilds
geometry procedurally and saves new source scenes, replacing manual model edits
for the selected assets.

Validation checks the packaged image sizes, alpha and occupied frame bounds,
animation differences, all manifest hashes, source-scene integrity, sprite
registration metadata, and the mod's generated prototype references. Supplying
`--blender` also opens every scene and checks editable geometry, materials,
orthographic cameras, lights, and missing dependencies. A Factorio data-stage
check and visual review in the game remain useful before publishing a release.

When changing a model, re-render its complete animation and all three passes.
Repack the collection so the derived icons, research art, sample images,
manifests, and gallery remain consistent. Do not edit the generated atlas images
or Lua metadata independently of their source scenes.
