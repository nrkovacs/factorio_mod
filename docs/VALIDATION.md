# Interstellar Fleets Validation

This document records the local checks used to validate the mod after source changes.

## Command-Line Smoke Tests

Use an isolated Factorio config so validation does not interfere with the user's normal saves or running game:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Factorio\bin\x64\factorio.exe' --config .\validation\isolated-config.ini --mod-directory .\dist --create .\validation\interstellar-fleets-test.zip
```

Then run a short runtime benchmark:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Factorio\bin\x64\factorio.exe' --config .\validation\isolated-config.ini --mod-directory .\dist --benchmark .\validation\interstellar-fleets-test.zip --benchmark-ticks 600
```

Passing these checks proves the data stage loads, all prototypes resolve, control scripts initialize, and the periodic runtime loop survives at least 600 updates.

Latest local run on 2026-06-08:

- `--create C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-tech-validator.zip`: passed with exit code 0 using a temporary data-stage validator for new technology unlocks, infinite research configuration, space-safe machine placement, and orbital-industry soft-lock checks.
- `--create C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-final-current.zip`: passed with exit code 0.
- `--benchmark C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-final-current.zip --benchmark-ticks 600`: passed with exit code 0, averaging 0.077 ms/update.
- `--benchmark C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-review-auto-boost.zip --benchmark-ticks 300`: passed with exit code 0 using the auto-boost validation companion mod.
- `--start-server C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-review-runtime.zip --until-tick 360`: passed with exit code 0 using the validation companion mod.
- `C:\Users\nrkov\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\validate_art_assets.py`: passed, confirming icon, technology, sprite-sheet, and GIF dimensions.
- `--create C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-custom-art.zip`: passed with exit code 0 after custom sprite-sheet integration.
- `--benchmark C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-custom-art.zip --benchmark-ticks 600`: passed with exit code 0, averaging 0.103 ms/update.

Latest Blender-rendered art run on 2026-06-09:

- `C:\tmp\blender-portable\blender-4.5.9-windows-x64\blender.exe --background --factory-startup --python scripts\blender_render_assets.py`: passed, rendering 36 transparent isometric frames for 9 custom assets.
- `C:\Users\nrkov\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\pack_blender_assets.py`: passed, packing Blender frames into icons, technology art, sprite sheets, glow masks, GIF previews, and `graphics/art-preview-sheet.png`.
- `C:\Users\nrkov\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\validate_art_assets.py`: passed, confirming all generated art dimensions and four-frame preview GIFs.
- `--create C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-blender-art.zip`: passed with exit code 0 after rebuilding the release zip with Blender-rendered art.
- `--benchmark C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-blender-art.zip --benchmark-ticks 600 --benchmark-verbose all`: passed with exit code 0, averaging 0.097 ms/update.

Latest Blender art refinement pass on 2026-06-09:

- Reviewed the existing preview sheet against Factorio's industrial visual style. The first Blender assets were readable but too clean and toy-like at icon scale.
- Generated A/B loop 1: `a-industrial` versus `b-arcology`. The industrial version fit Factorio better, but both needed stronger building-specific silhouettes.
- Generated A/B loop 2: `c-hero-industrial` versus `d-hero-neon`. `c-hero-industrial` won because it had better gritty mass, denser greebles, and clearer silhouettes; `d-hero-neon` was readable but too clean.
- Generated loop 3 final production hybrid using `c-hero-industrial` as the base, with brighter highlights and sharper post-processing for small icon readability.
- Final preview sheets were saved under `tmp\art-ab\` during local review and the selected production assets were packed into `graphics\`.
- `C:\Users\nrkov\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\validate_art_assets.py`: passed after final art refinement.
- `--create C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-art-refinement.zip`: passed with exit code 0 after rebuilding the final refined art zip.
- `--benchmark C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-art-refinement.zip --benchmark-ticks 600 --benchmark-verbose all`: passed with exit code 0, averaging 0.083 ms/update.

Latest hero-detail art pass on 2026-06-09:

- Added more artistically distinctive Blender geometry while keeping the silhouettes readable at Factorio icon scale.
- Interstellar labs gained sensor clusters, side radiators, a screen, and an observatory dish so they read as deep-space research infrastructure.
- Quantum replicators gained a larger matter gate, crystal cluster, side radiators, and orbiting particles so they read as exotic material printers.
- Dust collectors gained a wider dust-net ring, collector mast, and solar wing panels so they read as active deep-space harvesting equipment.
- Drives gained keel fins, heat shields, exhaust rings, and plasma feathers to make fusion and antimatter propulsion feel more powerful.
- Platform machines gained stronger identity details: foundry cranes and ore loader, electromagnetic coil bindings and diagonal arcs, biochamber nutrient tanks and glass equator, and cryogenic center tank plus frost crystals.
- `C:\Users\nrkov\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\validate_art_assets.py`: passed after the hero-detail art pass.
- `--create C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-hero-art.zip`: passed with exit code 0 after rebuilding the hero-detail art zip.
- `--benchmark C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-fleets-hero-art.zip --benchmark-ticks 600 --benchmark-verbose all`: passed with exit code 0, averaging 0.098 ms/update.

Latest interstellar lab reference-match pass on 2026-06-09:

- Downloaded and reviewed `graphics/previews/Interstellar_lab_reference.mp4`; the reference shows a space-platform lab with solar wings, satellite dishes, a glass research dome, purple research pulse, teal conduit glow, and steam plumes.
- Updated the Blender lab render to use a platform deck, readable solar-panel wings, larger dish antennas, teal deck traces, a hex-pattern research dome, a purple pulse cycle, and late-frame steam puffs.
- Generated `sound/interstellar-lab-working.ogg` as a short looping industrial research hum with scanner tones, dome pulse overtones, relay clicks, and steam hiss.
- `C:\tmp\blender-portable\blender-4.5.9-windows-x64\blender.exe --background --python scripts\blender_render_assets.py -- --variant production --out tmp\blender-renders interstellar-lab`: passed after rerendering the lab frames.
- `C:\Users\nrkov\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\pack_blender_assets.py`: passed after packing the updated lab sprite sheet, glow mask, icon, technology image, preview GIF, and art preview sheet.
- `C:\Users\nrkov\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\validate_art_assets.py`: passed, including the new OGG sound asset check.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build.ps1`: passed and rebuilt `dist\interstellar-fleets_0.1.0.zip` with the `sound` folder included.
- `--create C:\Users\nrkov\workspace\factorio_mod\validation\interstellar-lab-reference-test.zip`: passed with exit code 0 using the rebuilt package from `dist`.

## Soft-Lock Review

The intended recovery loop is:

1. Interstellar dust collectors script-generate `interstellar-dust` on fleet platforms.
2. Full hubs spill excess dust near the hub instead of deleting it.
3. Quantum replicators convert dust into raw resources, advanced construction parts, `fusion-power-cell`, `antimatter`, `biter-egg`, `pentapod-egg`, `bioflux`, Gleba crops, and `promethium-asteroid-chunk` after the relevant finite technologies.
4. Orbital industry unlocks space-safe interstellar foundries, electromagnetic plants, biochambers, and cryogenic plants with recipes made from interstellar dust and replicated resources, so planet-specific production chains can be rebuilt on-platform without importing the original planet-only machines.
5. Asteroid crushers can process dust through `interstellar-dust-crushing` and `advanced-interstellar-dust-crushing`, returning some dust and probabilistically producing asteroid chunks including rare promethium chunks.
6. Fusion drives consume `fusion-power-cell`; antimatter drives consume `antimatter`; auto boost can consume these fuels once per second without manual clicks.
7. Efficiency research lowers drive fuel cost but clamps at 20% of base cost, while other infinite research improves dust collection, quantum replication productivity, and fleet coordination.

This means a platform with a valid hub, at least one collector, power, and a quantum replicator can recover the critical consumables needed for interstellar progress. A platform with no hub, no collector, no power, or no replicator still needs player logistics intervention; those are normal Factorio construction failures rather than unrecoverable scripted fleet-state failures.

## Balance Review

- The mod starts after Promethium science, so all new systems are post-victory/endgame.
- Dust replication is broad enough to support interstellar self-sufficiency and all infinite science chains, but split across finite milestones and expensive enough to avoid replacing planet-scale production early.
- Stellar fusion drives are the baseline propulsion loop and use cheaper fusion cells.
- Antimatter drives provide four drive-power units each but require expensive replicated antimatter.
- Infinite drive-efficiency research gives a long-term science sink while preserving fuel logistics through a 20% minimum cost multiplier.
- Fleet scaling applies an aggregate speed and energy-consumption effect instead of duplicating entities, keeping the UPS goal aligned with the design.
