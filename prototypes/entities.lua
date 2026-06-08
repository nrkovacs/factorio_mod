local function copy_prototype(kind, source, name)
  local prototype = table.deepcopy(data.raw[kind][source])
  prototype.name = name
  prototype.minable = prototype.minable and table.deepcopy(prototype.minable) or nil
  if prototype.minable then
    prototype.minable.result = name
  end
  return prototype
end

local function tint_sprite_definitions(value, tint)
  if type(value) ~= "table" then
    return
  end

  if value.filename or value.filenames or value.stripes then
    value.tint = value.tint or tint
  end

  for _, child in pairs(value) do
    tint_sprite_definitions(child, tint)
  end
end

local lab = copy_prototype("lab", "biolab", "interstellar-lab")
lab.icon = "__interstellar-fleets__/graphics/icons/interstellar-lab.png"
lab.icon_size = 64
lab.energy_usage = "2MW"
lab.researching_speed = 2
lab.inputs = table.deepcopy(data.raw.lab.biolab.inputs)
lab.surface_conditions = nil
tint_sprite_definitions(lab, {r = 0.55, g = 0.9, b = 1.0, a = 1.0})

local replicator = copy_prototype("assembling-machine", "electromagnetic-plant", "quantum-replicator")
replicator.icon = "__interstellar-fleets__/graphics/icons/quantum-replicator.png"
replicator.icon_size = 64
replicator.crafting_categories = {"interstellar-replication"}
replicator.crafting_speed = 2
replicator.energy_usage = "15MW"
replicator.module_slots = 4
replicator.surface_conditions = nil
tint_sprite_definitions(replicator, {r = 0.75, g = 0.45, b = 1.0, a = 1.0})

local dust_collector = copy_prototype("asteroid-collector", "asteroid-collector", "interstellar-dust-collector")
dust_collector.icon = "__interstellar-fleets__/graphics/icons/interstellar-dust.png"
dust_collector.icon_size = 64
dust_collector.collection_box = {{-8, -8}, {8, 8}}
tint_sprite_definitions(dust_collector, {r = 1.0, g = 0.82, b = 0.35, a = 1.0})

local fusion_drive = copy_prototype("thruster", "thruster", "stellar-fusion-drive")
fusion_drive.icon = "__interstellar-fleets__/graphics/icons/stellar-fusion-drive.png"
fusion_drive.icon_size = 64
fusion_drive.min_performance = table.deepcopy(data.raw.thruster.thruster.min_performance)
fusion_drive.max_performance = table.deepcopy(data.raw.thruster.thruster.max_performance)
tint_sprite_definitions(fusion_drive, {r = 0.5, g = 0.85, b = 1.0, a = 1.0})

local antimatter_drive = copy_prototype("thruster", "thruster", "antimatter-drive")
antimatter_drive.icon = "__interstellar-fleets__/graphics/icons/antimatter-drive.png"
antimatter_drive.icon_size = 64
antimatter_drive.min_performance = table.deepcopy(data.raw.thruster.thruster.min_performance)
antimatter_drive.max_performance = table.deepcopy(data.raw.thruster.thruster.max_performance)
tint_sprite_definitions(antimatter_drive, {r = 0.78, g = 0.4, b = 1.0, a = 1.0})

local space_foundry = copy_prototype("assembling-machine", "foundry", "interstellar-foundry")
space_foundry.surface_conditions = nil
tint_sprite_definitions(space_foundry, {r = 0.55, g = 0.9, b = 1.0, a = 1.0})

local space_electromagnetic_plant = copy_prototype("assembling-machine", "electromagnetic-plant", "interstellar-electromagnetic-plant")
space_electromagnetic_plant.surface_conditions = nil
tint_sprite_definitions(space_electromagnetic_plant, {r = 0.75, g = 0.45, b = 1.0, a = 1.0})

local space_biochamber = copy_prototype("assembling-machine", "biochamber", "interstellar-biochamber")
space_biochamber.surface_conditions = nil
tint_sprite_definitions(space_biochamber, {r = 0.45, g = 1.0, b = 0.65, a = 1.0})

local space_cryogenic_plant = copy_prototype("assembling-machine", "cryogenic-plant", "interstellar-cryogenic-plant")
space_cryogenic_plant.surface_conditions = nil
tint_sprite_definitions(space_cryogenic_plant, {r = 0.55, g = 0.9, b = 1.0, a = 1.0})

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
  {
    type = "item",
    name = "interstellar-lab",
    icon = lab.icon,
    icon_size = 64,
    subgroup = "production-machine",
    order = "z[interstellar]-c[lab]",
    place_result = "interstellar-lab",
    stack_size = 10
  },
  {
    type = "item",
    name = "quantum-replicator",
    icon = replicator.icon,
    icon_size = 64,
    subgroup = "production-machine",
    order = "z[interstellar]-d[replicator]",
    place_result = "quantum-replicator",
    stack_size = 10
  },
  {
    type = "item",
    name = "interstellar-dust-collector",
    icon = dust_collector.icon,
    icon_size = 64,
    subgroup = "space-platform",
    order = "z[interstellar]-e[dust-collector]",
    place_result = "interstellar-dust-collector",
    stack_size = 10
  },
  {
    type = "item",
    name = "stellar-fusion-drive",
    icon = fusion_drive.icon,
    icon_size = 64,
    subgroup = "space-platform",
    order = "z[interstellar]-f[fusion-drive]",
    place_result = "stellar-fusion-drive",
    stack_size = 10
  },
  {
    type = "item",
    name = "antimatter-drive",
    icon = antimatter_drive.icon,
    icon_size = 64,
    subgroup = "space-platform",
    order = "z[interstellar]-g[antimatter-drive]",
    place_result = "antimatter-drive",
    stack_size = 10
  },
  {
    type = "item",
    name = "interstellar-foundry",
    icon = space_foundry.icon,
    icons = space_foundry.icons,
    icon_size = space_foundry.icon_size or 64,
    subgroup = "production-machine",
    order = "z[interstellar]-h[foundry]",
    place_result = "interstellar-foundry",
    stack_size = 10
  },
  {
    type = "item",
    name = "interstellar-electromagnetic-plant",
    icon = space_electromagnetic_plant.icon,
    icons = space_electromagnetic_plant.icons,
    icon_size = space_electromagnetic_plant.icon_size or 64,
    subgroup = "production-machine",
    order = "z[interstellar]-i[electromagnetic-plant]",
    place_result = "interstellar-electromagnetic-plant",
    stack_size = 10
  },
  {
    type = "item",
    name = "interstellar-biochamber",
    icon = space_biochamber.icon,
    icons = space_biochamber.icons,
    icon_size = space_biochamber.icon_size or 64,
    subgroup = "production-machine",
    order = "z[interstellar]-j[biochamber]",
    place_result = "interstellar-biochamber",
    stack_size = 10
  },
  {
    type = "item",
    name = "interstellar-cryogenic-plant",
    icon = space_cryogenic_plant.icon,
    icons = space_cryogenic_plant.icons,
    icon_size = space_cryogenic_plant.icon_size or 64,
    subgroup = "production-machine",
    order = "z[interstellar]-k[cryogenic-plant]",
    place_result = "interstellar-cryogenic-plant",
    stack_size = 10
  }
})
