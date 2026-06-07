local route_from = data.raw["space-location"]["shattered-planet"] and "shattered-planet" or "aquilo"

data:extend({
  {
    type = "space-location",
    name = "galactic-center",
    icon = "__base__/graphics/icons/space-science-pack.png",
    icon_size = 64,
    starmap_icon = "__base__/graphics/icons/space-science-pack.png",
    starmap_icon_size = 64,
    distance = 1000000000,
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
    icon = "__base__/graphics/icons/space-science-pack.png",
    icon_size = 64
  }
})
