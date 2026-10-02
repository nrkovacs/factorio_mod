-- Offline art-reference probe. This executes the mod's data stage with small
-- vanilla fixtures; it does not validate Factorio's complete prototype schema.
-- Run from the repository root: lua scripts/inspect_art_prototypes.lua

local function deepcopy(value, seen)
  if type(value) ~= "table" then return value end
  seen = seen or {}
  if seen[value] then return seen[value] end
  local result = {}
  seen[value] = result
  for key, item in pairs(value) do result[deepcopy(key, seen)] = deepcopy(item, seen) end
  return result
end
table.deepcopy = deepcopy

local function vanilla_sprite()
  return {filename = "__space-age__/graphics/fixture.png", width = 64, height = 64, frame_count = 1}
end

local function vanilla_machine(kind, name)
  local fixture = {
    type = kind, name = name,
    icon = "__space-age__/graphics/icons/" .. name .. ".png", icon_size = 64,
    minable = {result = name},
    crafting_categories = {"crafting"},
    collision_box = {{-1.4, -1.4}, {1.4, 1.4}},
    selection_box = {{-1.5, -1.5}, {1.5, 1.5}},
    on_animation = vanilla_sprite(), off_animation = vanilla_sprite(),
    graphics_set = {
      animation = vanilla_sprite(),
      idle_animation = vanilla_sprite(),
      working_visualisations = {{animation = vanilla_sprite()}}
    },
    pictures = vanilla_sprite(),
    working_sound = {
      sound = {filename = "__space-age__/sound/fixture.ogg"},
      sound_accents = {{sound = {filename = "__space-age__/sound/accent.ogg"}, frame = 52}}
    },
    drawing_box = {{-2, -3}, {2, 2}},
    fluid_boxes = {{pipe_connections = {{position = {0, -1}, direction = 0}}}},
    fluid_box = {pipe_connections = {{position = {0, -1}, direction = 0}}},
    energy_source = {type = "electric"},
    surface_conditions = {{property = "pressure", min = 4000}},
    plumes = {},
  }
  if kind == "asteroid-collector" then
    fixture.graphics_set.arm_head_animation = vanilla_sprite()
    fixture.graphics_set.arm_head_top_animation = vanilla_sprite()
    fixture.graphics_set.arm_link = vanilla_sprite()
  elseif kind == "thruster" then
    fixture.fuel_fluid_box = {pipe_connections = {
      {position = {-1.5, -2}, direction = 12, enable_working_visualisations = {"pipe-4"}},
      {position = {1.5, 0}, direction = 4, enable_working_visualisations = {"pipe-2"}}
    }}
    fixture.oxidizer_fluid_box = {pipe_connections = {
      {position = {1.5, -2}, direction = 4, enable_working_visualisations = {"pipe-1"}},
      {position = {-1.5, 0}, direction = 12, enable_working_visualisations = {"pipe-3"}}
    }}
    fixture.graphics_set.flame_effect = vanilla_sprite()
    fixture.graphics_set.flame_position = {0, 5.5}
    fixture.graphics_set.working_visualisations = {}
    for index = 1, 4 do
      table.insert(fixture.graphics_set.working_visualisations, {
        name = "pipe-" .. index, enabled_by_name = true, always_draw = true,
        animation = vanilla_sprite()
      })
    end
  end
  return fixture
end

data = {raw = {}, created = {}}
function data:extend(prototypes)
  for _, prototype in ipairs(prototypes) do
    assert(prototype.type and prototype.name, "prototype is missing its type or name")
    self.raw[prototype.type] = self.raw[prototype.type] or {}
    assert(not self.raw[prototype.type][prototype.name], "duplicate prototype: " .. prototype.name)
    self.raw[prototype.type][prototype.name] = prototype
    table.insert(self.created, prototype)
  end
end

local sources = {
  lab = {"biolab"},
  ["assembling-machine"] = {"electromagnetic-plant", "foundry", "biochamber", "cryogenic-plant"},
  ["asteroid-collector"] = {"asteroid-collector"},
  thruster = {"thruster"},
}
for kind, names in pairs(sources) do
  data.raw[kind] = {}
  for _, name in ipairs(names) do data.raw[kind][name] = vanilla_machine(kind, name) end
end
data.raw["space-location"] = {["shattered-planet"] = {name = "shattered-planet"}}
data.raw.recipe = {}
for _, name in ipairs({"metallurgic-science-pack", "electromagnetic-science-pack",
                       "agricultural-science-pack", "cryogenic-science-pack"}) do
  data.raw.recipe[name] = {
    type = "recipe", name = name, category = "crafting",
    ingredients = {}, results = {{type = "item", name = name, amount = 1}},
    energy_required = 10, allow_productivity = true,
    surface_conditions = {{property = "pressure", min = 1000}}
  }
end

-- The art module can use Factorio's ordinary cardinal direction constants.
defines = {direction = {north = 0, east = 4, south = 8, west = 12}}
util = {by_pixel = function(x, y) return {x / 32, y / 32} end}
package.preload["util"] = function() return util end
package.preload["__space-age__/prototypes/planet/asteroid-spawn-definitions"] = function()
  return {chunk_angle = 1, big_angle = 1, huge_angle = 1, spawn_definitions = function() return {} end}
end

require("data")

local function escape(value)
  local replacements = {["\""] = '\\"', ["\\"] = "\\\\", ["\n"] = "\\n", ["\r"] = "\\r", ["\t"] = "\\t"}
  return '"' .. value:gsub('["\\\n\r\t]', replacements) .. '"'
end

local function json(value)
  if type(value) == "string" then return escape(value) end
  if type(value) == "number" or type(value) == "boolean" then return tostring(value) end
  if value == nil then return "null" end
  assert(type(value) == "table", "unsupported JSON value: " .. type(value))
  local array, count = true, 0
  for key in pairs(value) do
    count = count + 1
    if type(key) ~= "number" or key < 1 or key % 1 ~= 0 then array = false end
  end
  array = array and count == #value
  local result = {}
  if array then
    for _, item in ipairs(value) do table.insert(result, json(item)) end
    return "[" .. table.concat(result, ",") .. "]"
  end
  local keys = {}
  for key in pairs(value) do table.insert(keys, key) end
  table.sort(keys)
  for _, key in ipairs(keys) do table.insert(result, escape(key) .. ":" .. json(value[key])) end
  return "{" .. table.concat(result, ",") .. "}"
end

print(json({prototypes = data.created, manifest = require("prototypes.art-manifest")}))
