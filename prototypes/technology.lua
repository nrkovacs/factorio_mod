data:extend({
  {
    type = "technology",
    name = "interstellar-fleets",
    icon = "__space-age__/graphics/technology/promethium-science-pack.png",
    icon_size = 256,
    prerequisites = {"promethium-science-pack"},
    unit = {
      count = 2000,
      ingredients = {
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
      },
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
    icon = "__space-age__/graphics/technology/quantum-processor.png",
    icon_size = 256,
    prerequisites = {"interstellar-fleets"},
    unit = {
      count = 3000,
      ingredients = {
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
      },
      time = 60
    },
    effects = {
      {type = "unlock-recipe", recipe = "quantum-replicator"},
      {type = "unlock-recipe", recipe = "dust-fusion-energy-cell"},
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
      {type = "unlock-recipe", recipe = "replicate-lithium"}
    }
  },
  {
    type = "technology",
    name = "fleet-printing",
    icon = "__space-age__/graphics/technology/foundation.png",
    icon_size = 256,
    prerequisites = {"quantum-replication"},
    unit = {
      count = 5000,
      ingredients = {
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
      },
      time = 60
    },
    effects = {
      {type = "unlock-recipe", recipe = "ship-starter-pack"},
      {type = "unlock-recipe", recipe = "antimatter-drive"}
    }
  }
})
