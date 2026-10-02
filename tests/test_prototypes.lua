-- Run from the repository root with Lua 5.2+: lua tests/test_prototypes.lua
-- Offline regression tests, not a substitute for Factorio's prototype loader.
local checks = 0
local function check(value, message)
  checks = checks + 1
  assert(value, message)
end

local function deepcopy(value)
  if type(value) ~= "table" then return value end
  local result = {}
  for key, child in pairs(value) do result[deepcopy(key)] = deepcopy(child) end
  return result
end
table.deepcopy = deepcopy

local function equal(left, right)
  if type(left) ~= type(right) then return false end
  if type(left) ~= "table" then return left == right end
  for key, value in pairs(left) do
    if not equal(value, right[key]) then return false end
  end
  for key in pairs(right) do
    if left[key] == nil then return false end
  end
  return true
end

local function contains(values, expected)
  for _, value in ipairs(values or {}) do
    if value == expected then return true end
  end
  return false
end

data = {raw = {recipe = {}, ["recipe-category"] = {}}}
function data:extend(prototypes)
  for _, prototype in ipairs(prototypes) do
    self.raw[prototype.type] = self.raw[prototype.type] or {}
    assert(not self.raw[prototype.type][prototype.name], "duplicate prototype: " .. prototype.name)
    self.raw[prototype.type][prototype.name] = prototype
  end
end

local science_machines = {
  {"metallurgic-science-pack", "foundry", "metallurgy", "pressure", 4000},
  {"electromagnetic-science-pack", "electromagnetic-plant", "electromagnetics", "magnetic-field", 99},
  {"agricultural-science-pack", "biochamber", "organic", "pressure", 2000},
  {"cryogenic-science-pack", "cryogenic-plant", "cryogenics", "pressure", 300}
}

-- Essential production fields from Wube's Factorio 2.0.72 recipes:
-- https://github.com/wube/factorio-data/blob/2.0.72/space-age/prototypes/recipe.lua
local science_inputs = {
  ["metallurgic-science-pack"] = {
    {type = "item", name = "tungsten-carbide", amount = 3},
    {type = "item", name = "tungsten-plate", amount = 2},
    {type = "fluid", name = "molten-copper", amount = 200}
  },
  ["electromagnetic-science-pack"] = {
    {type = "item", name = "supercapacitor", amount = 1},
    {type = "item", name = "accumulator", amount = 1},
    {type = "fluid", name = "electrolyte", amount = 25},
    {type = "fluid", name = "holmium-solution", amount = 25}
  },
  ["agricultural-science-pack"] = {
    {type = "item", name = "bioflux", amount = 1},
    {type = "item", name = "pentapod-egg", amount = 1}
  },
  ["cryogenic-science-pack"] = {
    {type = "item", name = "ice", amount = 3},
    {type = "item", name = "lithium-plate", amount = 1},
    {type = "fluid", name = "fluoroketone-cold", amount = 6, ignored_by_stats = 3}
  }
}
local science_times = {10, 10, 4, 20}
for index, definition in ipairs(science_machines) do
  local name, _, category, property, value = table.unpack(definition)
  local recipe = {
    type = "recipe", name = name, category = category, enabled = false,
    ingredients = deepcopy(science_inputs[name]),
    results = {{type = "item", name = name, amount = 1}},
    surface_conditions = {{property = property, min = value, max = value}},
    allow_productivity = true, energy_required = science_times[index]
  }
  if name == "cryogenic-science-pack" then
    recipe.main_product = name
    recipe.results[2] = {
      type = "fluid", name = "fluoroketone-hot", amount = 3,
      ignored_by_stats = 3, ignored_by_productivity = 3
    }
  end
  data:extend({recipe, {type = "recipe-category", name = category}})
end

local function machine(kind, name, categories)
  return {
    type = kind, name = name, icon = "__base__/graphics/icons/fixture.png", icon_size = 64,
    minable = {mining_time = 1, result = name},
    crafting_categories = categories,
    surface_conditions = {{property = "pressure", min = 1}},
    graphics_set = {animation = {layers = {
      {filename = "fixture.png", width = 32, height = 32},
      {filename = "shadow.png", width = 32, height = 32, draw_as_shadow = true}
    }}},
    working_sound = {sound = {filename = "fixture.ogg", volume = 0.5}}
  }
end
for _, definition in ipairs(science_machines) do
  data:extend({machine("assembling-machine", definition[2], {definition[3], "crafting"})})
end
data:extend({
  machine("lab", "biolab"),
  machine("asteroid-collector", "asteroid-collector"),
  machine("thruster", "thruster")
})
local original_recipes = deepcopy(data.raw.recipe)
local original_machines = deepcopy(data.raw["assembling-machine"])

dofile("prototypes/categories.lua")
dofile("prototypes/items.lua")
dofile("prototypes/entities.lua")
dofile("prototypes/recipes.lua")
dofile("prototypes/technology.lua")
dofile("prototypes/achievements.lua")
dofile("prototypes/shortcuts.lua")

local unlocks = {}
for _, effect in ipairs(data.raw.technology["orbital-industry"].effects) do
  if effect.type == "unlock-recipe" then unlocks[effect.recipe] = true end
end

for _, definition in ipairs(science_machines) do
  local source_name, machine_name, original_category = table.unpack(definition)
  local name = "interstellar-" .. source_name
  local category = "interstellar-" .. original_category
  local recipe = data.raw.recipe[name]
  check(recipe ~= nil, name .. " exists")
  check(recipe.surface_conditions == nil, name .. " works on platform surfaces")
  check(recipe.category == category, name .. " uses its exclusive category")
  check(data.raw["recipe-category"][category] ~= nil, category .. " is declared")
  check(recipe.enabled == false and unlocks[name], name .. " is gated by orbital industry")
  check(recipe.auto_recycle == false, name .. " does not add a reverse recipe")
  check(equal(recipe.localised_name, {"recipe-name." .. name}), name .. " has its own label")
  for _, field in ipairs({"ingredients", "results", "energy_required", "allow_productivity", "main_product"}) do
    check(equal(recipe[field], original_recipes[source_name][field]), name .. " preserves " .. field)
  end
  check(equal(data.raw.recipe[source_name], original_recipes[source_name]), source_name .. " is unchanged")
  check(recipe.ingredients ~= data.raw.recipe[source_name].ingredients, name .. " does not alias ingredients")
  check(recipe.results ~= data.raw.recipe[source_name].results, name .. " does not alias products")
  local interstellar_machine = data.raw["assembling-machine"]["interstellar-" .. machine_name]
  check(contains(interstellar_machine.crafting_categories, category), machine_name .. " variant accepts its new recipe")
  check(contains(interstellar_machine.crafting_categories, original_category), machine_name .. " variant keeps original recipes")
  check(interstellar_machine.surface_conditions == nil, machine_name .. " variant can be placed on platforms")
  for source_machine, original in pairs(original_machines) do
    check(equal(data.raw["assembling-machine"][source_machine], original), source_machine .. " is unchanged")
    check(not contains(data.raw["assembling-machine"][source_machine].crafting_categories, category), source_machine .. " cannot bypass vanilla recipe restrictions")
  end
end

-- Quality generates recycling for any eligible recipe regardless of unlock.
-- Every dust conversion must opt out or it can overwrite item-name-recycling
-- recipes for vanilla ores, components, and biological items.
local replication_count = 0
for name, recipe in pairs(data.raw.recipe) do
  if recipe.category == "interstellar-replication" then
    replication_count = replication_count + 1
    check(recipe.auto_recycle == false, name .. " must not replace vanilla recycling")
  end
end
check(replication_count == 24, "all 24 dust conversion recipes are covered")

for name, technology in pairs(data.raw.technology) do
  for _, effect in ipairs(technology.effects or {}) do
    if effect.type == "unlock-recipe" or effect.type == "change-recipe-productivity" then
      check(data.raw.recipe[effect.recipe] ~= nil, name .. " references an existing recipe")
    end
  end
end
for name, item in pairs(data.raw.item) do
  if item.place_result then
    local found = false
    for _, kind in ipairs({"lab", "assembling-machine", "asteroid-collector", "simple-entity-with-owner"}) do
      found = found or (data.raw[kind] or {})[item.place_result] ~= nil
    end
    check(found, name .. " places an existing entity")
  end
end

local replicator = data.raw["assembling-machine"]["quantum-replicator"]
check(equal(replicator.crafting_categories, {"interstellar-replication"}), "replicator is not a general-purpose electromagnetic plant")
check(replicator.graphics_set.animation.layers[1].tint ~= nil, "entity sprite is tinted")
check(replicator.graphics_set.animation.layers[2].tint == nil, "shadow is not tinted")
check(replicator.working_sound.sound.tint == nil, "sound is not treated as a sprite")
for _, name in ipairs({"stellar-fusion-drive", "antimatter-drive"}) do
  check(data.raw["simple-entity-with-owner"][name] ~= nil, name .. " uses the static drive type")
  check(data.raw.thruster[name] == nil, name .. " does not inherit fluid fuel requirements")
end

print("Prototype regression checks passed: " .. checks)
