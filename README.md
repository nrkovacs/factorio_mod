# Interstellar Fleets

Interstellar Fleets is an endgame Factorio: Space Age mod for players who have reached Promethium science and want a larger post-Shattered Planet objective without simulating hundreds of duplicate space platforms. It adds a deep-space fleet layer built around interstellar dust harvesting, quantum replication, relativistic drives, and a UPS-friendly fleet multiplier system.

The core idea is simple: once a platform design is stable, you can merge additional identical ships into a single represented fleet. The game keeps simulating one platform surface, while the mod tracks a fleet size multiplier and applies the benefits where they matter. This keeps the fantasy of operating a large interstellar armada without forcing Factorio to run every ship as a separate platform with duplicated machines, belts, inserters, collectors, and labs.

## Gameplay Summary

The mod extends Space Age after Promethium science with a new interstellar progression arc.

First, `Interstellar fleets` unlocks interstellar labs, interstellar dust collectors, stellar fusion drives, and a very long route toward the Galactic Center. The Galactic Center is intentionally extreme: it is far away, solar power is weak, and the route is effectively a late-game endurance project rather than a normal planet hop.

Interstellar dust collectors gather `interstellar-dust` while installed on space platforms. Runtime dust income scales with the platform fleet size and current relativistic speed, so a consolidated fleet still behaves like many ships harvesting dust without requiring every duplicate ship to exist as a fully simulated platform.

`Quantum replication` unlocks the quantum replicator and dust-based recipes for raw materials. Replicators convert interstellar dust into ores and other Space Age raw resources such as iron ore, copper ore, coal, stone, uranium ore, carbon, ice, scrap, calcite, tungsten ore, holmium ore, lithium, yumako, jellynut, bioflux, biter eggs, pentapod eggs, and promethium asteroid chunks. They also create antimatter through an intentionally expensive recipe that consumes a large quantity of interstellar dust plus fusion power cells. This gives interstellar platforms a way to become more self-sufficient once they can sustain dust collection and energy production, including a way to bootstrap biological science inputs and biter eggs from scratch without importing them from Nauvis or Gleba.

`Interstellar dust crushing` unlocks an asteroid-crusher recipe that reprocesses dust back into dust while occasionally exposing metallic, carbonic, oxide, and rare promethium asteroid chunks. This gives players a more Factorio-native alternative to direct promethium chunk replication: build crushers, handle probabilistic outputs, and sort mixed asteroid materials on-platform.

`Fleet printing` unlocks ship starter packs and antimatter drives. A ship starter pack represents the cost of adding one more matching platform to the fleet. Stellar fusion drives consume fusion power cells for dependable acceleration. Antimatter drives consume replicated antimatter and provide much stronger thrust, turning antimatter production into the premium fuel loop for high-speed interstellar travel. The fleet UI includes an auto-boost toggle so mature platforms can automate acceleration instead of requiring repeated manual boost clicks.

## Fleet Consolidation

Use the `Interstellar fleets` shortcut or `SHIFT + I` while standing on a space platform to open the fleet interface.

The interface exposes four actions:

- `Merge ship`: consumes one `ship-starter-pack` from the platform hub and increases fleet size by one.
- `Split fleet`: divides the current fleet roughly in half and creates a new platform for the split-off ships.
- `Update blueprint`: records the current platform layout as the fleet's matching layout.
- `Boost`: consumes fusion power cells and/or antimatter to increase fleet speed based on installed drives.
- `Auto boost`: toggles continuous once-per-second boosting while drives and matching fuel are available, pausing silently when fuel runs short.

Merge protection is intentionally strict. The mod records a compact signature of the represented platform layout. If the platform changes after consolidation, further merging is blocked until you either update the blueprint or split the fleet. This prevents a fleet of supposedly identical ships from silently drifting out of sync with the one platform that Factorio is actually simulating.

Splitting a fleet clears partial crafting and research progress on the original platform before creating the new split platform. That tradeoff keeps the system deterministic and avoids duplicating in-progress machine state.

## New Content

- `Interstellar dust`: exotic deep-space material gathered by fleet collectors.
- `Interstellar lab`: advanced research building whose research speed is boosted by fleet scaling.
- `Quantum replicator`: production machine for dust-to-resource conversion.
- `Interstellar dust collector`: upgraded collector for deep-space dust harvesting.
- `Stellar fusion drive`: blue-glow relativistic drive for fleet acceleration.
- `Antimatter`: expensive replicated drive fuel made from interstellar dust and fusion power cells, now represented by a distinct containment-capsule icon instead of reusing the antimatter drive art.
- `Antimatter drive`: purple high-output drive with stronger acceleration and separate antimatter fuel.
- `Ship starter pack`: expensive platform package consumed when merging ships into a fleet.
- `Galactic Center`: a distant Space Age location and long-haul objective beyond normal platform logistics.
- Expanded quantum replication inputs: yumako, jellynut, bioflux, pentapod eggs, and promethium asteroid chunks so mature platforms can continue all infinite science chains aboard interstellar fleets.
- `Interstellar dust crushing`: asteroid-crusher recipe that recovers part of the dust input and rolls for metallic, carbonic, oxide, and promethium asteroid chunks.

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
- Fusion acceleration consumes fusion power cells; antimatter acceleration consumes expensive replicated antimatter.
- Infinite drive-efficiency research reduces boost fuel costs over time: stellar fusion drive efficiency reduces fusion-cell cost by 8% per level, and antimatter drive efficiency reduces antimatter cost by 10% per level. Both efficiency chains floor at 20% of the original cost so high-speed travel remains a logistics problem.
- Acceleration becomes harder at high relativistic speed.
- The Galactic Center route is extremely long and low-solar, making ship design, fuel logistics, and fleet scaling matter.

The goal is not to trivialize Space Age. The goal is to give mature megabases a new scaling problem after normal planetary expansion is solved.

## Current Implementation Notes

- Fleet state is stored in Factorio `storage` by platform index.
- The represented platform receives surface-level speed and energy-consumption effects based on fleet size, approximating the throughput and power draw of the abstract ships.
- Dust collection, auto boost, and distance advancement run periodically in `control.lua`.
- Dust overflow is spilled near the platform hub instead of being deleted, so a full hub does not permanently waste the fleet's recovery resource.
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
- `docs/VALIDATION.md`: command-line validation steps, soft-lock review, and balance notes.
