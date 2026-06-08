# Interstellar Fleets PRD

## Overview

Interstellar Fleets is an endgame Space Age expansion focused on scaling very large Factorio factories without simulating thousands of duplicate machines. Players consolidate identical interstellar ships into fleets where one platform represents many identical copies.

## Goals

- Provide UPS-friendly production scaling through fleet multipliers.
- Add a Galactic Center destination at an extreme distance.
- Add a peaceful interstellar journey loop based on speed, energy investment, and dust collection.
- Let ships become self-sufficient through interstellar labs, dust collectors, and quantum replicators.

## Requirements

- A fleet has a size and represents identical copies of the same platform blueprint.
- Fleet merge consumes a ship starter pack and records or verifies a platform signature.
- Fleet blueprint update records the current platform layout as the new identical design and clears partial progress.
- Fleet split divides the fleet size in half and clears partial crafting progress.
- Interstellar dust collection scales with platform speed, dust collectors, and fleet size.
- Replicators convert interstellar dust into raw materials.
- Interstellar labs allow research aboard deep-space platforms.
- Interstellar drives allow acceleration toward a light-speed limit, with acceleration decreasing as speed approaches `c`.
- Stellar fusion drive boosting consumes fusion power cells from the platform hub, with cost increasing by fleet size and Lorentz factor.
- Antimatter drive boosting consumes replicated antimatter from the platform hub and provides stronger acceleration than stellar fusion drives.
- Infinite efficiency research must improve stellar fusion and antimatter drive fuel efficiency without removing fuel logistics entirely.
- Interstellar platforms must have a dust-based path to recover key consumables, including fusion power cells, antimatter, biter eggs, biological science inputs, and promethium asteroid chunks.
- A mature interstellar platform should be able to keep all infinite science research running by replicating missing source materials and producing science packs aboard the fleet.
- Galactic Center is unlocked through the interstellar tech tree.

## Open Question Resolutions

- Engine acquisition starts with stellar fusion drives, then antimatter drives through fleet printing.
- Antimatter is created by quantum replication from interstellar dust and fusion power cells.
- Replication has two tiers: basic dust conversion, then fleet printing with ship starter packs and antimatter propulsion.
- Speed is capped below light speed and uses a Lorentz-style curve for diminishing acceleration.
- The tech tree starts after Promethium science to keep the mod firmly post-victory.
