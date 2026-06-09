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

local replication_productivity_effects = {
  {type = "change-recipe-productivity", recipe = "dust-fusion-energy-cell", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-antimatter", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-iron-ore", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-copper-ore", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-coal", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-stone", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-uranium-ore", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-carbon", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-ice", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-scrap", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-calcite", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-tungsten-ore", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-holmium-ore", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-lithium", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-yumako", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-jellynut", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-bioflux", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-biter-egg", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-pentapod-egg", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-promethium-asteroid-chunk", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-processing-unit", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-low-density-structure", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-superconductor", change = 0.04},
  {type = "change-recipe-productivity", recipe = "replicate-quantum-processor", change = 0.04}
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
      {type = "unlock-recipe", recipe = "replicate-promethium-asteroid-chunk"}
    }
  },
  {
    type = "technology",
    name = "antimatter-containment",
    icon = "__interstellar-fleets__/graphics/technology/antimatter-containment.png",
    icon_size = 64,
    prerequisites = {"quantum-replication"},
    unit = {
      count = 4000,
      ingredients = late_science,
      time = 60
    },
    effects = {
      {type = "unlock-recipe", recipe = "replicate-antimatter"}
    }
  },
  {
    type = "technology",
    name = "interstellar-xenobiology",
    icon = "__interstellar-fleets__/graphics/technology/interstellar-xenobiology.png",
    icon_size = 64,
    prerequisites = {"quantum-replication"},
    unit = {
      count = 3500,
      ingredients = late_science,
      time = 60
    },
    effects = {
      {type = "unlock-recipe", recipe = "replicate-yumako"},
      {type = "unlock-recipe", recipe = "replicate-jellynut"},
      {type = "unlock-recipe", recipe = "replicate-bioflux"},
      {type = "unlock-recipe", recipe = "replicate-biter-egg"},
      {type = "unlock-recipe", recipe = "replicate-pentapod-egg"}
    }
  },
  {
    type = "technology",
    name = "quantum-fabrication",
    icon = "__interstellar-fleets__/graphics/technology/quantum-fabrication.png",
    icon_size = 64,
    prerequisites = {"quantum-replication"},
    unit = {
      count = 4500,
      ingredients = late_science,
      time = 60
    },
    effects = {
      {type = "unlock-recipe", recipe = "replicate-processing-unit"},
      {type = "unlock-recipe", recipe = "replicate-low-density-structure"},
      {type = "unlock-recipe", recipe = "replicate-superconductor"},
      {type = "unlock-recipe", recipe = "replicate-quantum-processor"}
    }
  },
  {
    type = "technology",
    name = "orbital-industry",
    icon = "__interstellar-fleets__/graphics/technology/orbital-industry.png",
    icon_size = 64,
    prerequisites = {"quantum-fabrication"},
    unit = {
      count = 5000,
      ingredients = late_science,
      time = 60
    },
    effects = {
      {type = "unlock-recipe", recipe = "interstellar-foundry"},
      {type = "unlock-recipe", recipe = "interstellar-electromagnetic-plant"},
      {type = "unlock-recipe", recipe = "interstellar-biochamber"},
      {type = "unlock-recipe", recipe = "interstellar-cryogenic-plant"}
    }
  },
  {
    type = "technology",
    name = "fleet-printing",
    icon = "__interstellar-fleets__/graphics/technology/fleet-printing.png",
    icon_size = 64,
    prerequisites = {"antimatter-containment", "orbital-industry"},
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
    name = "interstellar-dust-crushing",
    icon = "__interstellar-fleets__/graphics/technology/interstellar-dust-crushing.png",
    icon_size = 64,
    prerequisites = {"quantum-replication"},
    unit = {
      count = 2500,
      ingredients = late_science,
      time = 60
    },
    effects = {
      {type = "unlock-recipe", recipe = "interstellar-dust-crushing"}
    }
  },
  {
    type = "technology",
    name = "deep-dust-prospecting",
    icon = "__interstellar-fleets__/graphics/technology/deep-dust-prospecting.png",
    icon_size = 64,
    prerequisites = {"interstellar-dust-crushing"},
    unit = {
      count = 4000,
      ingredients = late_science,
      time = 60
    },
    effects = {
      {type = "unlock-recipe", recipe = "advanced-interstellar-dust-crushing"}
    }
  },
  {
    type = "technology",
    name = "stellar-fusion-drive-efficiency",
    icon = "__interstellar-fleets__/graphics/technology/stellar-fusion-drive-efficiency.png",
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
    name = "interstellar-dust-collection-productivity",
    icon = "__interstellar-fleets__/graphics/technology/interstellar-dust-collection-productivity.png",
    icon_size = 64,
    prerequisites = {"interstellar-fleets"},
    upgrade = true,
    max_level = "infinite",
    unit = {
      count_formula = "1200 * 1.45 ^ (L - 1)",
      ingredients = late_science,
      time = 60
    },
    effects = {}
  },
  {
    type = "technology",
    name = "quantum-replication-productivity",
    icon = "__interstellar-fleets__/graphics/technology/quantum-replication-productivity.png",
    icon_size = 64,
    prerequisites = {"quantum-replication"},
    upgrade = true,
    max_level = "infinite",
    unit = {
      count_formula = "1500 * 1.5 ^ (L - 1)",
      ingredients = late_science,
      time = 60
    },
    effects = replication_productivity_effects
  },
  {
    type = "technology",
    name = "fleet-coordination",
    icon = "__interstellar-fleets__/graphics/technology/fleet-coordination.png",
    icon_size = 64,
    prerequisites = {"fleet-printing"},
    upgrade = true,
    max_level = "infinite",
    unit = {
      count_formula = "2000 * 1.55 ^ (L - 1)",
      ingredients = late_science,
      time = 60
    },
    effects = {}
  },
  {
    type = "technology",
    name = "antimatter-drive-efficiency",
    icon = "__interstellar-fleets__/graphics/technology/antimatter-drive-efficiency.png",
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
