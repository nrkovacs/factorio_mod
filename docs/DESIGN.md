# Interstellar Fleets Design

## Architecture

The mod is split into data-stage prototypes and runtime fleet simulation.

- `prototypes/locations.lua` defines the Galactic Center and a very long Space Age route.
- `prototypes/entities.lua` defines interstellar labs, dust collectors, replicators, drives, and space-safe production-machine variants by extending Space Age prototypes.
- `prototypes/recipes.lua` defines dust conversion and fleet construction recipes.
- `control.lua` stores fleet state in `storage.fleets` keyed by `LuaSpacePlatform.index`.

## Runtime Systems

Fleet state:

```lua
storage.fleets[platform_index] = {
  size = 1,
  speed_c = 0.01,
  distance_m = 0,
  blueprint_hash = nil
}
```

Every 60 ticks, the runtime loop:

- Applies `LuaSurface.global_effect` on each platform surface so production machines and labs receive a speed bonus based on fleet size. Infinite fleet-coordination research increases this speed bonus without increasing the fleet-size power penalty. The effect is only written when the computed value changes, so idle and size-1 platforms are never touched and effects applied by other mods are not stomped every second.
- Inserts interstellar dust into the platform hub based on collector count, speed, and fleet size. Overflow that does not fit in the hub is buffered in a bounded per-fleet backlog (never spilled as ground items, which would create one entity per item and destroy UPS at fleet scale); the backlog drains into the hub as space frees up and collection pauses while the backlog is full.
- Advances abstract interstellar distance by `speed_c * c`.
- Refreshes open fleet management GUIs.

## Merge And Split

Merging computes a platform signature from player-force entities on the platform, ignoring transient entities such as cargo pods, construction ghosts, robots, corpses, and spilled items so in-transit deliveries and in-progress hub construction do not spuriously change the layout. The first merge records the signature; later merges require the same signature. A merge consumes one ship starter pack and increments fleet size.

Updating the blueprint stores the current platform signature as the fleet design and clears partial progress. This is the lightweight implementation of propagating an upgraded ship layout across abstract copies.

Splitting halves fleet size, clears partial progress on production entities, creates a new platform when possible, clones the source platform layout into it, and copies speed, distance, and blueprint signature to the split fleet. The new platform is created at the fleet's current location when Factorio allows it, falling back to Nauvis orbit for locations that cannot host a stationary platform (such as fly-condition destinations).

Boosting counts stellar fusion drives and antimatter drives, consumes the matching fuel from the platform hub, then applies diminishing acceleration using the current Lorentz factor. Stellar fusion drives add one drive-power unit each and consume `fusion-power-cell`; antimatter drives add four drive-power units each and consume `antimatter`.

Players can either click `Boost` manually or enable `Auto boost` in the fleet GUI. Auto boost attempts the same boost calculation once per second, consumes fuel only when a boost succeeds, and pauses quietly when drives or fuel are missing. This keeps acceleration automatable without accidentally deleting fuel or spamming warnings.

Several infinite technologies extend the fleet loop. `stellar-fusion-drive-efficiency` reduces fusion power cell costs by 8% per completed level, and `antimatter-drive-efficiency` reduces antimatter costs by 10% per completed level. Both chains clamp at a 20% minimum fuel-cost multiplier so late research rewards sustained investment without making propulsion free. `interstellar-dust-collection-productivity` increases scripted dust output by 8% per level, `quantum-replication-productivity` adds 4% productivity per level to replication recipes, and `fleet-coordination` improves the fleet-size speed bonus by 3% per level.

Quantum replication includes recovery recipes for the interstellar fuel and science loops. A stranded platform that still has a powered quantum replicator and dust collection can convert dust into fusion power cells, antimatter, biter eggs, pentapod eggs, bioflux, Gleba crops, promethium asteroid chunks, advanced construction parts, and raw resources. This keeps fuel starvation and missing-source-material science stalls from becoming permanent once the player has built the intended interstellar infrastructure.

`interstellar-dust-crushing` and `advanced-interstellar-dust-crushing` use the Space Age `crushing` category so normal asteroid crushers can process dust. The basic recipe consumes 100 dust, returns 60 dust, and independently rolls for metallic, carbonic, oxide, and rare promethium asteroid chunks. The advanced recipe consumes 200 dust, returns 120 dust, and improves chunk odds. Productivity is disabled on both recipes to avoid an infinite positive-feedback dust loop.

The shattered planet to galactic center connection defines its own asteroid spawn curve rather than leaving the route empty. Density starts comparable to the shattered planet approach, falls to roughly a quarter of that by the 100,000 km mark, and keeps thinning by a smaller factor each decade of distance, ending about 135 times sparser than departure. Promethium dominates the mix on departure and gives way to ordinary asteroid types further out. Because the base-game helper normalizes type ratios against the largest entry, promethium's share is walked down gently; dropping it faster renormalizes the other types upward and stalls their decline mid-route. The thinning is what forces a deep-space fleet off asteroid capture and onto dust harvesting and quantum replication.

`orbital-industry` unlocks interstellar foundry, electromagnetic plant, biochamber, and cryogenic plant variants. The mod copies the Space Age machines and clears their surface conditions instead of changing vanilla machines globally, so existing planet-locked buildings keep their normal rules while interstellar platforms get expensive dedicated versions. Their recipes use interstellar dust and resources unlocked through quantum replication, so a mature platform with a working replicator can rebuild them without importing the original planet-only machines.

## UPS Strategy

The implementation avoids duplicating entities for each ship copy. Fleet size affects script-generated outputs and aggregate lab speed, while the visible platform remains a single simulated platform.
