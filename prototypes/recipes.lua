local replication_recipes = {
  {"replicate-iron-ore", "iron-ore", 20, 10},
  {"replicate-copper-ore", "copper-ore", 20, 10},
  {"replicate-coal", "coal", 20, 10},
  {"replicate-stone", "stone", 20, 10},
  {"replicate-uranium-ore", "uranium-ore", 60, 5},
  {"replicate-carbon", "carbon", 30, 10},
  {"replicate-ice", "ice", 30, 10},
  {"replicate-scrap", "scrap", 60, 5},
  {"replicate-calcite", "calcite", 40, 5},
  {"replicate-tungsten-ore", "tungsten-ore", 80, 5},
  {"replicate-holmium-ore", "holmium-ore", 80, 5},
  {"replicate-lithium", "lithium", 80, 5},
  {"replicate-yumako", "yumako", 100, 5},
  {"replicate-jellynut", "jellynut", 100, 5},
  {"replicate-bioflux", "bioflux", 200, 2},
  {"replicate-biter-egg", "biter-egg", 120, 1},
  {"replicate-pentapod-egg", "pentapod-egg", 240, 1},
  {"replicate-promethium-asteroid-chunk", "promethium-asteroid-chunk", 300, 5}
}

local recipes = {
  {
    type = "recipe",
    name = "interstellar-lab",
    enabled = false,
    energy_required = 20,
    ingredients = {
      {type = "item", name = "biolab", amount = 1},
      {type = "item", name = "quantum-processor", amount = 50},
      {type = "item", name = "superconductor", amount = 100}
    },
    results = {{type = "item", name = "interstellar-lab", amount = 1}}
  },
  {
    type = "recipe",
    name = "quantum-replicator",
    enabled = false,
    energy_required = 30,
    ingredients = {
      {type = "item", name = "electromagnetic-plant", amount = 1},
      {type = "item", name = "quantum-processor", amount = 100},
      {type = "item", name = "superconductor", amount = 200}
    },
    results = {{type = "item", name = "quantum-replicator", amount = 1}}
  },
  {
    type = "recipe",
    name = "interstellar-dust-collector",
    enabled = false,
    energy_required = 15,
    ingredients = {
      {type = "item", name = "asteroid-collector", amount = 1},
      {type = "item", name = "quantum-processor", amount = 25},
      {type = "item", name = "low-density-structure", amount = 100}
    },
    results = {{type = "item", name = "interstellar-dust-collector", amount = 1}}
  },
  {
    type = "recipe",
    name = "stellar-fusion-drive",
    enabled = false,
    energy_required = 30,
    ingredients = {
      {type = "item", name = "thruster", amount = 1},
      {type = "item", name = "fusion-generator", amount = 2},
      {type = "item", name = "quantum-processor", amount = 50}
    },
    results = {{type = "item", name = "stellar-fusion-drive", amount = 1}}
  },
  {
    type = "recipe",
    name = "antimatter-drive",
    enabled = false,
    energy_required = 60,
    ingredients = {
      {type = "item", name = "stellar-fusion-drive", amount = 1},
      {type = "item", name = "quantum-processor", amount = 250},
      {type = "item", name = "superconductor", amount = 500}
    },
    results = {{type = "item", name = "antimatter-drive", amount = 1}}
  },
  {
    type = "recipe",
    name = "ship-starter-pack",
    enabled = false,
    energy_required = 120,
    ingredients = {
      {type = "item", name = "space-platform-foundation", amount = 1000},
      {type = "item", name = "stellar-fusion-drive", amount = 4},
      {type = "item", name = "interstellar-lab", amount = 4},
      {type = "item", name = "quantum-replicator", amount = 2}
    },
    results = {{type = "item", name = "ship-starter-pack", amount = 1}}
  },
  {
    type = "recipe",
    name = "dust-fusion-energy-cell",
    category = "interstellar-replication",
    enabled = false,
    energy_required = 10,
    ingredients = {{type = "item", name = "interstellar-dust", amount = 50}},
    results = {{type = "item", name = "fusion-power-cell", amount = 1}}
  },
  {
    type = "recipe",
    name = "replicate-antimatter",
    category = "interstellar-replication",
    enabled = false,
    energy_required = 120,
    ingredients = {
      {type = "item", name = "interstellar-dust", amount = 2000},
      {type = "item", name = "fusion-power-cell", amount = 10}
    },
    results = {{type = "item", name = "antimatter", amount = 1}}
  }
}

for _, recipe in pairs(replication_recipes) do
  recipes[#recipes + 1] = {
    type = "recipe",
    name = recipe[1],
    category = "interstellar-replication",
    enabled = false,
    energy_required = recipe[3],
    ingredients = {{type = "item", name = "interstellar-dust", amount = recipe[3]}},
    results = {{type = "item", name = recipe[2], amount = recipe[4]}}
  }
end

data:extend(recipes)
