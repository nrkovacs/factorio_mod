local late_science = {
  {"automation-science-pack", 1},
  {"logistic-science-pack", 1},
  {"chemical-science-pack", 1},
  {"production-science-pack", 1},
  {"utility-science-pack", 1},
  {"space-science-pack", 1},
  {"metallurgic-science-pack", 1},
  {"electromagnetic-science-pack", 1},
  {"agricultural-science-pack", 1},
  {"cryogenic-science-pack", 1},
  {"promethium-science-pack", 1}
}

data:extend({
  {
    type = "technology",
    name = "interstellar-fleets",
    icon = "__interstellar-fleets__/graphics/technology/interstellar-fleets.png",
    icon_size = 64,
    prerequisites = {"promethium-science-pack"},
    unit = {
      count = 2000,
      ingredients = late_science,
      time = 60
    },
    effects = {
      {type = "unlock-recipe", recipe = "interstellar-lab"},
      {type = "unlock-recipe", recipe = "interstellar-dust-collector"},
      {type = "unlock-recipe", recipe = "stellar-fusion-drive"},
      {type = "unlock-space-location", space_location = "galactic-center"}
    }
  },
  {
    type = "technology",
    name = "quantum-replication",
    icon = "__interstellar-fleets__/graphics/technology/quantum-replication.png",
    icon_size = 64,
    prerequisites = {"interstellar-fleets"},
    unit = {
      count = 3000,
      ingredients = late_science,
      time = 60
    },
    effects = {
      {type = "unlock-recipe", recipe = "quantum-replicator"},
      {type = "unlock-recipe", recipe = "dust-fusion-energy-cell"},
      {type = "unlock-recipe", recipe = "replicate-antimatter"},
      {type = "unlock-recipe", recipe = "replicate-iron-ore"},
      {type = "unlock-recipe", recipe = "replicate-copper-ore"},
      {type = "unlock-recipe", recipe = "replicate-coal"},
      {type = "unlock-recipe", recipe = "replicate-stone"},
      {type = "unlock-recipe", recipe = "replicate-uranium-ore"},
      {type = "unlock-recipe", recipe = "replicate-carbon"},
      {type = "unlock-recipe", recipe = "replicate-ice"},
      {type = "unlock-recipe", recipe = "replicate-scrap"},
      {type = "unlock-recipe", recipe = "replicate-calcite"},
      {type = "unlock-recipe", recipe = "replicate-tungsten-ore"},
      {type = "unlock-recipe", recipe = "replicate-holmium-ore"},
      {type = "unlock-recipe", recipe = "replicate-lithium"},
      {type = "unlock-recipe", recipe = "replicate-yumako"},
      {type = "unlock-recipe", recipe = "replicate-jellynut"},
      {type = "unlock-recipe", recipe = "replicate-bioflux"},
      {type = "unlock-recipe", recipe = "replicate-biter-egg"},
      {type = "unlock-recipe", recipe = "replicate-pentapod-egg"},
      {type = "unlock-recipe", recipe = "replicate-promethium-asteroid-chunk"}
    }
  },
  {
    type = "technology",
    name = "fleet-printing",
    icon = "__interstellar-fleets__/graphics/technology/fleet-printing.png",
    icon_size = 64,
    prerequisites = {"quantum-replication"},
    unit = {
      count = 5000,
      ingredients = late_science,
      time = 60
    },
    effects = {
      {type = "unlock-recipe", recipe = "ship-starter-pack"},
      {type = "unlock-recipe", recipe = "antimatter-drive"}
    }
  },
  {
    type = "technology",
    name = "stellar-fusion-drive-efficiency",
    icon = "__interstellar-fleets__/graphics/technology/interstellar-fleets.png",
    icon_size = 64,
    prerequisites = {"interstellar-fleets"},
    upgrade = true,
    max_level = "infinite",
    unit = {
      count_formula = "1000 * 1.5 ^ (L - 1)",
      ingredients = late_science,
      time = 60
    },
    effects = {}
  },
  {
    type = "technology",
    name = "antimatter-drive-efficiency",
    icon = "__interstellar-fleets__/graphics/technology/fleet-printing.png",
    icon_size = 64,
    prerequisites = {"fleet-printing", "stellar-fusion-drive-efficiency"},
    upgrade = true,
    max_level = "infinite",
    unit = {
      count_formula = "1500 * 1.6 ^ (L - 1)",
      ingredients = late_science,
      time = 60
    },
    effects = {}
  }
})
