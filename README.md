# Interstellar Fleets

Interstellar Fleets is an endgame Factorio: Space Age mod that lets players consolidate identical space platforms into UPS-friendly fleets. A fleet is simulated as one platform with a fleet size multiplier for interstellar dust collection and interstellar lab output.

## Current Gameplay

- Unlock the interstellar tech tree after Promethium science.
- Travel toward the Galactic Center through a long asteroid-free route.
- Build interstellar dust collectors to gather dust proportional to fleet speed.
- Use quantum replicators to convert interstellar dust into raw materials.
- Use ship starter packs to merge identical ships into larger fleets.
- Fleet size applies a platform-surface speed effect so machines aboard the represented ship scale without simulating duplicate ships.
- Split fleets in half; partial crafting and research progress on the original platform is cleared.
- Use the Interstellar Fleets shortcut or `SHIFT + I` while on a platform to manage a fleet.

## Files

- `info.json`: mod metadata and Space Age dependency.
- `prototypes/`: items, entities, recipes, technologies, shortcuts, and space locations.
- `control.lua`: runtime fleet state, GUI, merge/split, dust collection, and lab multiplier logic.
- `docs/PRD.md`: product requirements derived from the original brainstorming conversation.
- `docs/DESIGN.md`: implementation design for the current mod architecture.
