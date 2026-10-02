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

-- Validate the *real* prototypes after Space Age and Quality have loaded. This
-- catches ignored graphics properties as well as loss of native ports or arms;
-- the Python asset audit separately checks the referenced PNG bytes and bounds.
local art_manifest = require("__interstellar-fleets__.prototypes.art-manifest")
local art_root = "__interstellar-fleets__/graphics/"
local function same(left, right)
  if type(left) ~= type(right) then return false end
  if type(left) ~= "table" then return left == right end
  for key, value in pairs(left) do if not same(value, right[key]) then return false end end
  for key in pairs(right) do if left[key] == nil then return false end end
  return true
end

local function check_sprite(sprite, name, layer, direction, idle)
  local spec = art_manifest[name]
  assert(sprite and sprite.filename == art_root .. "entity/" .. name .. "/" .. name .. "-" .. layer .. ".png",
    name .. " must use the custom " .. layer .. " atlas")
  assert(sprite.width == spec.width and sprite.height == spec.height, name .. " frame dimensions disagree with manifest")
  assert(sprite.frame_count == (idle and 1 or spec.frame_count), name .. " frame count disagrees with manifest")
  assert(sprite.line_length == spec.line_length and sprite.scale == spec.scale and same(sprite.shift, spec.shift),
    name .. " atlas layout or placement disagrees with manifest")
  assert((sprite.y or 0) == (direction - 1) * spec.height * math.ceil(spec.frame_count / spec.line_length),
    name .. " reads the wrong direction row")
  assert((sprite.draw_as_shadow == true) == (layer == "shadow"), name .. " shadow pass is incorrect")
  assert((sprite.draw_as_glow == true) == (layer == "glow"), name .. " emission pass is incorrect")
  if layer == "glow" then assert(sprite.blend_mode == "additive", name .. " emission must be additive") end
end

local function check_animation(animation, name, direction, glow, idle)
  assert(animation and animation.layers and #animation.layers == (glow and 3 or 2), name .. " has missing art layers")
  check_sprite(animation.layers[1], name, "animation", direction, idle)
  check_sprite(animation.layers[2], name, "shadow", direction, idle)
  if glow then check_sprite(animation.layers[3], name, "glow", direction, idle) end
end

local function connection_visual_names(value, names)
  if type(value) ~= "table" then return end
  for _, name in ipairs(value.enable_working_visualisations or {}) do names[name] = true end
  for _, child in pairs(value) do connection_visual_names(child, names) end
end

local machines = {
  {"lab", "interstellar-lab", "lab", "biolab"},
  {"assembling-machine", "quantum-replicator", "assembling-machine", "electromagnetic-plant"},
  {"asteroid-collector", "interstellar-dust-collector", "asteroid-collector", "asteroid-collector"},
  {"simple-entity-with-owner", "stellar-fusion-drive", "thruster", "thruster"},
  {"simple-entity-with-owner", "antimatter-drive", "thruster", "thruster"},
  {"assembling-machine", "interstellar-foundry", "assembling-machine", "foundry"},
  {"assembling-machine", "interstellar-electromagnetic-plant", "assembling-machine", "electromagnetic-plant"},
  {"assembling-machine", "interstellar-biochamber", "assembling-machine", "biochamber"},
  {"assembling-machine", "interstellar-cryogenic-plant", "assembling-machine", "cryogenic-plant"}
}
for _, row in ipairs(machines) do
  local kind, name, source_kind, source_name = table.unpack(row)
  local entity, source = data.raw[kind][name], data.raw[source_kind][source_name]
  assert(entity.icons and #entity.icons == 1 and entity.icons[1].icon == art_root .. "icons/" .. name .. ".png",
    name .. " entity icon must match its model")
  assert(same(data.raw.item[name].icons, entity.icons), name .. " item and entity icons disagree")
  for _, field in ipairs({"collision_box", "selection_box", "tile_buildability_rules"}) do
    assert(same(entity[field], source[field]), name .. " art changed its placement footprint")
  end
  if kind == "lab" then
    check_animation(entity.on_animation, name, 1, true)
    check_animation(entity.off_animation, name, 1, false, true)
  elseif kind == "simple-entity-with-owner" then
    check_animation(entity.animations, name, 1, true)
    assert(not entity.picture and not entity.pictures, name .. " art is hidden by a higher-priority sprite field")
    assert(not entity.fuel_fluid_box and not entity.oxidizer_fluid_box and not data.raw.thruster[name],
      name .. " must keep item-fueled drive behavior")
  elseif kind == "asteroid-collector" then
    for direction, key in ipairs({"north", "east", "south", "west"}) do
      check_animation(entity.graphics_set.animation[key], name, direction, true)
    end
    for _, field in ipairs({"arm_link", "arm_head_animation", "arm_head_top_animation"}) do
      assert(source.graphics_set[field] and same(entity.graphics_set[field], source.graphics_set[field]),
        name .. " native articulated arm graphics changed")
    end
    assert(not entity.graphics_set.below_arm_pictures and not entity.graphics_set.below_ground_pictures,
      name .. " retains an obsolete vanilla body overlay")
    assert(same(entity.circuit_connector, source.circuit_connector), name .. " circuit connectors changed")
  else
    check_animation(entity.graphics_set.animation, name, 1, false)
    assert(not entity.animation and not entity.graphics_set_flipped and not entity.graphics_set.frozen_patch,
      name .. " retains obsolete body graphics")
    assert(same(entity.fluid_boxes, source.fluid_boxes), name .. " fluid connections changed")
    assert(same(entity.circuit_connector, source.circuit_connector), name .. " circuit connectors changed")
    local connection_names, retained_connections = {}, {}
    connection_visual_names(source.fluid_boxes, connection_names)
    local emission_count = 0
    for _, visual in ipairs(entity.graphics_set.working_visualisations) do
      if visual.name then retained_connections[visual.name] = visual end
      if visual.animation and visual.animation.filename == art_root .. "entity/" .. name .. "/" .. name .. "-glow.png" then
        emission_count = emission_count + 1
        check_sprite(visual.animation, name, "glow", 1)
        assert(not visual.always_draw, name .. " process glow must follow machine activity")
      end
    end
    assert(emission_count == 1, name .. " needs exactly one process glow")
    for _, visual in ipairs(source.graphics_set.working_visualisations or {}) do
      if visual.name and connection_names[visual.name] then
        assert(same(retained_connections[visual.name], visual), name .. " lost a native pipe connection overlay")
      end
    end
  end
end
log("INTERSTELLAR_FLEETS_ART_PROTOTYPE_TESTS_PASSED")
log("INTERSTELLAR_FLEETS_PROTOTYPE_TESTS_PASSED")
