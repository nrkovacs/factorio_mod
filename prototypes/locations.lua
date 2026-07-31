local route_from = data.raw["space-location"]["shattered-planet"] and "shattered-planet" or "aquilo"

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
    icon_size = 64
  }
})
