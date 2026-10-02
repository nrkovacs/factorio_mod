local variants = {
  {"metallurgic-science-pack", "interstellar-foundry", "foundry"},
  {"electromagnetic-science-pack", "interstellar-electromagnetic-plant", "electromagnetic-plant"},
  {"agricultural-science-pack", "interstellar-biochamber", "biochamber"},
  {"cryogenic-science-pack", "interstellar-cryogenic-plant", "cryogenic-plant"}
}
local function contains(list, value)
  for _, entry in pairs(list) do if entry == value then return true end end
  return false
end
for _, row in ipairs(variants) do
  local source = data.raw.recipe[row[1]]
  local orbital = data.raw.recipe["interstellar-" .. row[1]]
  assert(source.surface_conditions and #source.surface_conditions > 0, "vanilla science restrictions changed")
  assert(orbital and not orbital.surface_conditions, "orbital science remains surface restricted")
  assert(contains(data.raw["assembling-machine"][row[2]].crafting_categories, orbital.category), "orbital machine lacks category")
  assert(not contains(data.raw["assembling-machine"][row[3]].crafting_categories, orbital.category), "vanilla machine gained orbital category")
end
for name, recipe in pairs(data.raw.recipe) do
  if name:find("^replicate%-") then assert(recipe.auto_recycle == false, "replication auto recycling enabled") end
end
local iron_recycling = data.raw.recipe["iron-ore-recycling"]
if iron_recycling then
  for _, product in pairs(iron_recycling.results or {}) do
    assert(product.name ~= "interstellar-dust", "vanilla iron ore recycling replaced by dust recipe")
  end
end
log("INTERSTELLAR_FLEETS_PROTOTYPE_TESTS_PASSED")
