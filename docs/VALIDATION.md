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

Latest local run on 2026-06-07:

- `--create .\validation\interstellar-fleets-split-fix-test.zip`: passed with exit code 0.
- `--benchmark .\validation\interstellar-fleets-split-fix-test.zip --benchmark-ticks 600`: passed with exit code 0, averaging 0.084 ms/update.

## Soft-Lock Review

The intended recovery loop is:

1. Interstellar dust collectors script-generate `interstellar-dust` on fleet platforms.
2. Full hubs spill excess dust near the hub instead of deleting it.
3. Quantum replicators convert dust into raw resources, `fusion-power-cell`, `antimatter`, `biter-egg`, `pentapod-egg`, `bioflux`, Gleba crops, and `promethium-asteroid-chunk`.
4. Fusion drives consume `fusion-power-cell`; antimatter drives consume `antimatter`.
5. Efficiency research lowers drive fuel cost but clamps at 20% of base cost.

This means a platform with a valid hub, at least one collector, power, and a quantum replicator can recover the critical consumables needed for interstellar progress. A platform with no hub, no collector, no power, or no replicator still needs player logistics intervention; those are normal Factorio construction failures rather than unrecoverable scripted fleet-state failures.

## Balance Review

- The mod starts after Promethium science, so all new systems are post-victory/endgame.
- Dust replication is broad enough to support interstellar self-sufficiency and all infinite science chains, but expensive enough to avoid replacing planet-scale production early.
- Stellar fusion drives are the baseline propulsion loop and use cheaper fusion cells.
- Antimatter drives provide four drive-power units each but require expensive replicated antimatter.
- Infinite drive-efficiency research gives a long-term science sink while preserving fuel logistics through a 20% minimum cost multiplier.
- Fleet scaling applies an aggregate speed and energy-consumption effect instead of duplicating entities, keeping the UPS goal aligned with the design.
