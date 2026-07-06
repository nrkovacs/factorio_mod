local function copy_prototype(kind, source, name)
  local prototype = table.deepcopy(data.raw[kind][source])
  prototype.name = name
  if prototype.minable then
    prototype.minable.result = name
  end
  return prototype
end

local function is_sound_definition(value)
  local filename = value.filename
  return type(filename) == "string" and (filename:find("%.ogg$") or filename:find("%.wav$")) ~= nil
end

local function tint_sprite_definitions(value, tint)
  if type(value) ~= "table" then
    return
  end

  if (value.filename or value.filenames or value.stripes)
      and not value.draw_as_shadow
      and not is_sound_definition(value) then
    value.tint = value.tint or tint
  end

  for _, child in pairs(value) do
    tint_sprite_definitions(child, tint)
  end
end

-- Reuse the source machine's base-game icon with the same tint as its entity
-- graphics, so items, recipes, and placed entities stay visually consistent.
local function apply_tint(prototype, tint)
  tint_sprite_definitions(prototype, tint)

  local icons
  if prototype.icons then
    icons = table.deepcopy(prototype.icons)
    for _, layer in pairs(icons) do
      layer.tint = layer.tint or tint
    end
  else
    icons = {{icon = prototype.icon, icon_size = prototype.icon_size or 64, tint = tint}}
  end
  prototype.icon = nil
  prototype.icon_size = nil
  prototype.icons = icons
end

local lab = copy_prototype("lab", "biolab", "interstellar-lab")
lab.energy_usage = "2MW"
lab.researching_speed = 2
lab.surface_conditions = nil
lab.working_sound = {
  sound = {
    filename = "__interstellar-fleets__/sound/interstellar-lab-working.ogg",
    volume = 0.72
  },
  apparent_volume = 1.2,
  audible_distance_modifier = 0.7,
  fade_in_ticks = 20,
  fade_out_ticks = 40
}
apply_tint(lab, {r = 0.55, g = 0.9, b = 1.0, a = 1.0})

local replicator = copy_prototype("assembling-machine", "electromagnetic-plant", "quantum-replicator")
replicator.crafting_categories = {"interstellar-replication"}
replicator.crafting_speed = 2
replicator.energy_usage = "15MW"
replicator.module_slots = 4
replicator.effect_receiver = nil
replicator.surface_conditions = nil
apply_tint(replicator, {r = 0.75, g = 0.45, b = 1.0, a = 1.0})

local dust_collector = copy_prototype("asteroid-collector", "asteroid-collector", "interstellar-dust-collector")
dust_collector.collection_radius = 8
apply_tint(dust_collector, {r = 1.0, g = 0.82, b = 0.35, a = 1.0})

local fusion_drive = copy_prototype("thruster", "thruster", "stellar-fusion-drive")
apply_tint(fusion_drive, {r = 0.5, g = 0.85, b = 1.0, a = 1.0})

local antimatter_drive = copy_prototype("thruster", "thruster", "antimatter-drive")
apply_tint(antimatter_drive, {r = 0.78, g = 0.4, b = 1.0, a = 1.0})

local space_foundry = copy_prototype("assembling-machine", "foundry", "interstellar-foundry")
space_foundry.surface_conditions = nil
apply_tint(space_foundry, {r = 0.55, g = 0.9, b = 1.0, a = 1.0})

local space_electromagnetic_plant = copy_prototype("assembling-machine", "electromagnetic-plant", "interstellar-electromagnetic-plant")
space_electromagnetic_plant.surface_conditions = nil
apply_tint(space_electromagnetic_plant, {r = 0.75, g = 0.45, b = 1.0, a = 1.0})

local space_biochamber = copy_prototype("assembling-machine", "biochamber", "interstellar-biochamber")
space_biochamber.surface_conditions = nil
apply_tint(space_biochamber, {r = 0.45, g = 1.0, b = 0.65, a = 1.0})

local space_cryogenic_plant = copy_prototype("assembling-machine", "cryogenic-plant", "interstellar-cryogenic-plant")
space_cryogenic_plant.surface_conditions = nil
apply_tint(space_cryogenic_plant, {r = 0.55, g = 0.9, b = 1.0, a = 1.0})

local function machine_item(entity, subgroup, order)
  return {
    type = "item",
    name = entity.name,
    icons = table.deepcopy(entity.icons),
    subgroup = subgroup,
    order = order,
    place_result = entity.name,
    stack_size = 10
  }
end

data:extend({
  lab,
  replicator,
  dust_collector,
  fusion_drive,
  antimatter_drive,
  space_foundry,
  space_electromagnetic_plant,
  space_biochamber,
  space_cryogenic_plant,
  machine_item(lab, "production-machine", "z[interstellar]-c[lab]"),
  machine_item(replicator, "production-machine", "z[interstellar]-d[replicator]"),
  machine_item(dust_collector, "space-platform", "z[interstellar]-e[dust-collector]"),
  machine_item(fusion_drive, "space-platform", "z[interstellar]-f[fusion-drive]"),
  machine_item(antimatter_drive, "space-platform", "z[interstellar]-g[antimatter-drive]"),
  machine_item(space_foundry, "production-machine", "z[interstellar]-h[foundry]"),
  machine_item(space_electromagnetic_plant, "production-machine", "z[interstellar]-i[electromagnetic-plant]"),
  machine_item(space_biochamber, "production-machine", "z[interstellar]-j[biochamber]"),
  machine_item(space_cryogenic_plant, "production-machine", "z[interstellar]-k[cryogenic-plant]")
})
