# Interstellar Fleets

Interstellar Fleets is an endgame Factorio: Space Age mod for players who have reached Promethium science and want a larger post-Shattered Planet objective without simulating hundreds of duplicate space platforms. It adds a deep-space fleet layer built around interstellar dust harvesting, quantum replication, relativistic drives, and a UPS-friendly fleet multiplier system.

The core idea is simple: once a platform design is stable, you can merge additional identical ships into a single represented fleet. The game keeps simulating one platform surface, while the mod tracks a fleet size multiplier and applies the benefits where they matter. This keeps the fantasy of operating a large interstellar armada without forcing Factorio to run every ship as a separate platform with duplicated machines, belts, inserters, collectors, and labs.

## Gameplay Summary

The mod extends Space Age after Promethium science with a new interstellar progression arc.

First, `Interstellar fleets` unlocks interstellar labs, interstellar dust collectors, stellar fusion drives, and a very long route toward the Galactic Center. The Galactic Center is intentionally extreme: it is far away, solar power is weak, and the route is effectively a late-game endurance project rather than a normal planet hop.

Interstellar dust collectors gather `interstellar-dust` while installed on space platforms. Runtime dust income scales with the platform fleet size and current relativistic speed, so a consolidated fleet still behaves like many ships harvesting dust without requiring every duplicate ship to exist as a fully simulated platform.

`Quantum replication` unlocks the quantum replicator and dust-based recipes for raw materials. Replicators convert interstellar dust into ores and other Space Age raw resources such as iron ore, copper ore, coal, stone, uranium ore, carbon, ice, scrap, calcite, tungsten ore, holmium ore, and lithium. This gives interstellar platforms a way to become more self-sufficient once they can sustain dust collection and energy production.

`Fleet printing` unlocks ship starter packs and antimatter drives. A ship starter pack represents the cost of adding one more matching platform to the fleet. Antimatter drives provide stronger acceleration than stellar fusion drives and push fleet travel further into the relativistic endgame.

## Fleet Consolidation

Use the `Interstellar fleets` shortcut or `SHIFT + I` while standing on a space platform to open the fleet interface.

The interface exposes four actions:

- `Merge ship`: consumes one `ship-starter-pack` from the platform hub and increases fleet size by one.
- `Split fleet`: divides the current fleet roughly in half and creates a new platform for the split-off ships.
- `Update blueprint`: records the current platform layout as the fleet's matching layout.
- `Boost`: consumes fusion power cells to increase fleet speed based on installed drives.

Merge protection is intentionally strict. The mod records a compact signature of the represented platform layout. If the platform changes after consolidation, further merging is blocked until you either update the blueprint or split the fleet. This prevents a fleet of supposedly identical ships from silently drifting out of sync with the one platform that Factorio is actually simulating.

Splitting a fleet clears partial crafting and research progress on the original platform before creating the new split platform. That tradeoff keeps the system deterministic and avoids duplicating in-progress machine state.

## New Content

- `Interstellar dust`: exotic deep-space material gathered by fleet collectors.
- `Interstellar lab`: advanced research building whose productivity is boosted by fleet scaling.
- `Quantum replicator`: production machine for dust-to-resource conversion.
- `Interstellar dust collector`: upgraded collector for deep-space dust harvesting.
- `Stellar fusion drive`: blue-glow relativistic drive for fleet acceleration.
- `Antimatter drive`: purple high-output drive with stronger acceleration.
- `Ship starter pack`: expensive platform package consumed when merging ships into a fleet.
- `Galactic Center`: a distant Space Age location and long-haul objective beyond normal platform logistics.

## Art Direction

The mod now includes generated custom artwork for its thumbnail, item icons, and technology icons:

- `thumbnail.png` shows an industrial fleet approaching a bright galactic core.
- `graphics/icons/` contains distinct generated icons for dust, starter packs, labs, replicators, and both drive tiers.
- `graphics/technology/` reuses selected generated icons at technology scale.

Placed entities still reuse Space Age base animations because those are reliable, animated, and already aligned to Factorio's entity geometry. The prototypes apply color tinting to distinguish the new machines in-world: cyan for interstellar labs and fusion drives, violet for quantum/antimatter equipment, and gold for dust collection. I did not reuse images or animations from third-party mods because their licenses are unknown; the implementation sticks to original generated static art plus Factorio/Space Age dependency assets.

## Balance Intent

Interstellar Fleets is deliberately late-game:

- Research begins after Promethium science.
- Recipes require expensive Space Age intermediates.
- Fleet merging consumes ship starter packs instead of being free.
- Acceleration consumes fusion power cells and becomes harder at high relativistic speed.
- The Galactic Center route is extremely long and low-solar, making ship design, fuel logistics, and fleet scaling matter.

The goal is not to trivialize Space Age. The goal is to give mature megabases a new scaling problem after normal planetary expansion is solved.

## Current Implementation Notes

- Fleet state is stored in Factorio `storage` by platform index.
- The represented platform receives surface-level productivity and speed effects based on fleet size.
- Dust collection and acceleration run periodically in `control.lua`.
- Merge/split operations are exposed through a custom GUI and shortcut.
- Platform layout matching uses a deterministic signature over non-character, non-resource entities.
- Split fleets clone the represented platform layout when Factorio can create the destination platform.

## Files

- `info.json`: mod metadata and Space Age dependency.
- `thumbnail.png`: mod thumbnail.
- `graphics/`: generated icon and technology artwork.
- `prototypes/`: items, entities, recipes, technologies, shortcuts, and space locations.
- `locale/`: player-facing names and descriptions.
- `control.lua`: runtime fleet state, GUI, merge/split, dust collection, acceleration, and fleet multipliers.
- `docs/PRD.md`: product requirements derived from the original brainstorming conversation.
- `docs/DESIGN.md`: implementation design for the current mod architecture.
