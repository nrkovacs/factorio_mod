local asteroid_util = require("__space-age__/prototypes/planet/asteroid-spawn-definitions")

local route_from = data.raw["space-location"]["shattered-planet"] and "shattered-planet" or "aquilo"

-- Asteroid density along the run to the galactic center. Positions are a
-- fraction of the 1e9 km connection, so 0.0001 is the 100,000 km mark.
--
-- The route leaves the shattered planet at roughly the density ships are used
-- to there, thins out sharply over the first 100,000 km, and then keeps
-- thinning by a smaller factor each decade of distance. Deep space never goes
-- completely empty, but past the 100,000 km mark asteroids are rare enough
-- that a fleet cannot live off collectors and crushers alone -- which is the
-- point where dust harvesting and quantum replication have to take over.
--
-- Every probability table shares the same positions as type_ratios: the
-- base-game interpolation helper looks up the surrounding point in each table
-- independently and has no fallback when one table starts later than another.
local GALACTIC_CENTER_ASTEROIDS = {
  has_promethium_asteroids = true,
  probability_on_range_chunk = {
    {position = 0.00001, probability = 0.00060, angle_when_stopped = asteroid_util.chunk_angle},
    {position = 0.0001,  probability = 0.00015, angle_when_stopped = asteroid_util.chunk_angle},
    {position = 0.001,   probability = 0.00006, angle_when_stopped = asteroid_util.chunk_angle},
    {position = 0.01,    probability = 0.00002, angle_when_stopped = asteroid_util.chunk_angle},
    {position = 0.1,     probability = 0.00001, angle_when_stopped = asteroid_util.chunk_angle},
    {position = 0.999, probability = 0.000004, angle_when_stopped = asteroid_util.chunk_angle}
  },
  probability_on_range_big = {
    {position = 0.00001, probability = 0.00200, angle_when_stopped = asteroid_util.big_angle},
    {position = 0.0001,  probability = 0.00050, angle_when_stopped = asteroid_util.big_angle},
    {position = 0.001,   probability = 0.00020, angle_when_stopped = asteroid_util.big_angle},
    {position = 0.01,    probability = 0.00008, angle_when_stopped = asteroid_util.big_angle},
    {position = 0.1,     probability = 0.00003, angle_when_stopped = asteroid_util.big_angle},
    {position = 0.999, probability = 0.00001, angle_when_stopped = asteroid_util.big_angle}
  },
  probability_on_range_huge = {
    {position = 0.00001, probability = 0.09000, angle_when_stopped = asteroid_util.huge_angle},
    {position = 0.0001,  probability = 0.02000, angle_when_stopped = asteroid_util.huge_angle},
    {position = 0.001,   probability = 0.00800, angle_when_stopped = asteroid_util.huge_angle},
    {position = 0.01,    probability = 0.00300, angle_when_stopped = asteroid_util.huge_angle},
    {position = 0.1,     probability = 0.00120, angle_when_stopped = asteroid_util.huge_angle},
    {position = 0.999, probability = 0.00040, angle_when_stopped = asteroid_util.huge_angle}
  },
  -- Promethium keeps the dominant share on departure to match the shattered
  -- planet, then gives way to ordinary asteroid types as the fleet gets out.
  -- Ratios are normalized against the largest entry, so promethium's share is
  -- walked down gently: dropping it faster would renormalize the other types
  -- upward and stall their decline in the middle of the route.
  type_ratios = {
    {position = 0.00001, ratios = {10, 2, 4, 164.03}},
    {position = 0.0001,  ratios = {10, 3, 5, 120}},
    {position = 0.001,   ratios = {10, 4, 6,  80}},
    {position = 0.01,    ratios = {10, 5, 7,  50}},
    {position = 0.1,     ratios = { 8, 5, 6,  30}},
    {position = 0.999,   ratios = { 6, 5, 5,  20}}
  }
}

data:extend({
  {
    type = "space-location",
    name = "galactic-center",
    icon = "__interstellar-fleets__/graphics/icons/interstellar-dust.png",
    icon_size = 64,
    starmap_icon = "__interstellar-fleets__/graphics/icons/interstellar-dust.png",
    starmap_icon_size = 64,
    -- Starmap placement only. Vanilla locations sit at distance 10-80
    -- (shattered-planet is 80); a huge value here pushes the icon so far
    -- off the starmap that the destination cannot be seen or selected.
    -- The extreme journey length lives on the space-connection below.
    distance = 120,
    orientation = 0.72,
    magnitude = 2.5,
    draw_orbit = false,
    solar_power_in_space = 0.05,
    asteroid_spawn_influence = 0,
    fly_condition = true
  },
  {
    type = "space-connection",
    name = route_from .. "-galactic-center",
    from = route_from,
    to = "galactic-center",
    length = 1000000000,
    icon = "__interstellar-fleets__/graphics/icons/interstellar-dust.png",
    icon_size = 64,
    asteroid_spawn_definitions = asteroid_util.spawn_definitions(GALACTIC_CENTER_ASTEROIDS)
  }
})
