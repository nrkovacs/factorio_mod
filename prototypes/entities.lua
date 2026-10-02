local art = require("prototypes.art")

local function copy_prototype(kind, source, name)
  local prototype = table.deepcopy(data.raw[kind][source])
  prototype.name = name
  if prototype.minable then
    prototype.minable.result = name
  end
  return prototype
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
art.apply_lab(lab)

local replicator = copy_prototype("assembling-machine", "electromagnetic-plant", "quantum-replicator")
replicator.crafting_categories = {"interstellar-replication"}
replicator.crafting_speed = 2
replicator.energy_usage = "15MW"
replicator.module_slots = 4
replicator.effect_receiver = nil
replicator.surface_conditions = nil
art.apply_crafting_machine(replicator)

local dust_collector = copy_prototype("asteroid-collector", "asteroid-collector", "interstellar-dust-collector")
dust_collector.collection_radius = 8
art.apply_collector(dust_collector)

-- Drives are fueled by items (fusion power cells / antimatter) pulled from the
-- hub during fleet boosts in control.lua, so they must not inherit the vanilla
-- thruster's thruster-fuel/oxidizer fluid boxes. Build them as static
-- structures that reuse the thruster's platform placement rules.
local function make_drive(name)
  local thruster = data.raw["thruster"]["thruster"]
  return {
    type = "simple-entity-with-owner",
    name = name,
    flags = table.deepcopy(thruster.flags),
    icon = thruster.icon,
    icon_size = thruster.icon_size,
    collision_box = table.deepcopy(thruster.collision_box),
    collision_mask = table.deepcopy(thruster.collision_mask),
    selection_box = table.deepcopy(thruster.selection_box),
    tile_buildability_rules = table.deepcopy(thruster.tile_buildability_rules),
    surface_conditions = table.deepcopy(thruster.surface_conditions),
    max_health = thruster.max_health,
    minable = {mining_time = 0.1, result = name},
    impact_category = thruster.impact_category,
    corpse = thruster.corpse,
    dying_explosion = thruster.dying_explosion,
    placeable_position_visualization = table.deepcopy(thruster.placeable_position_visualization),
    animations = table.deepcopy(thruster.graphics_set.animation)
  }
end

local fusion_drive = make_drive("stellar-fusion-drive")
art.apply_drive(fusion_drive)

local antimatter_drive = make_drive("antimatter-drive")
art.apply_drive(antimatter_drive)

local space_foundry = copy_prototype("assembling-machine", "foundry", "interstellar-foundry")
space_foundry.surface_conditions = nil
table.insert(space_foundry.crafting_categories, "interstellar-metallurgy")
art.apply_crafting_machine(space_foundry)

local space_electromagnetic_plant = copy_prototype("assembling-machine", "electromagnetic-plant", "interstellar-electromagnetic-plant")
space_electromagnetic_plant.surface_conditions = nil
table.insert(space_electromagnetic_plant.crafting_categories, "interstellar-electromagnetics")
art.apply_crafting_machine(space_electromagnetic_plant)

local space_biochamber = copy_prototype("assembling-machine", "biochamber", "interstellar-biochamber")
space_biochamber.surface_conditions = nil
table.insert(space_biochamber.crafting_categories, "interstellar-organic")
art.apply_crafting_machine(space_biochamber)

local space_cryogenic_plant = copy_prototype("assembling-machine", "cryogenic-plant", "interstellar-cryogenic-plant")
space_cryogenic_plant.surface_conditions = nil
table.insert(space_cryogenic_plant.crafting_categories, "interstellar-cryogenics")
art.apply_crafting_machine(space_cryogenic_plant)

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
