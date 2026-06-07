local function copy_prototype(kind, source, name)
  local prototype = table.deepcopy(data.raw[kind][source])
  prototype.name = name
  prototype.minable = prototype.minable and table.deepcopy(prototype.minable) or nil
  if prototype.minable then
    prototype.minable.result = name
  end
  return prototype
end

local lab = copy_prototype("lab", "biolab", "interstellar-lab")
lab.icon = "__space-age__/graphics/icons/biolab.png"
lab.energy_usage = "2MW"
lab.researching_speed = 2
lab.inputs = table.deepcopy(data.raw.lab.biolab.inputs)
lab.surface_conditions = nil

local replicator = copy_prototype("assembling-machine", "electromagnetic-plant", "quantum-replicator")
replicator.icon = "__space-age__/graphics/icons/electromagnetic-plant.png"
replicator.crafting_categories = {"interstellar-replication"}
replicator.crafting_speed = 2
replicator.energy_usage = "15MW"
replicator.module_slots = 4
replicator.surface_conditions = nil

local dust_collector = copy_prototype("asteroid-collector", "asteroid-collector", "interstellar-dust-collector")
dust_collector.icon = "__space-age__/graphics/icons/asteroid-collector.png"
dust_collector.collection_box = {{-8, -8}, {8, 8}}

local fusion_drive = copy_prototype("thruster", "thruster", "stellar-fusion-drive")
fusion_drive.icon = "__space-age__/graphics/icons/thruster.png"
fusion_drive.min_performance = table.deepcopy(data.raw.thruster.thruster.min_performance)
fusion_drive.max_performance = table.deepcopy(data.raw.thruster.thruster.max_performance)

local antimatter_drive = copy_prototype("thruster", "thruster", "antimatter-drive")
antimatter_drive.icon = "__space-age__/graphics/icons/thruster.png"
antimatter_drive.min_performance = table.deepcopy(data.raw.thruster.thruster.min_performance)
antimatter_drive.max_performance = table.deepcopy(data.raw.thruster.thruster.max_performance)

data:extend({
  lab,
  replicator,
  dust_collector,
  fusion_drive,
  antimatter_drive,
  {
    type = "item",
    name = "interstellar-lab",
    icon = lab.icon,
    subgroup = "production-machine",
    order = "z[interstellar]-c[lab]",
    place_result = "interstellar-lab",
    stack_size = 10
  },
  {
    type = "item",
    name = "quantum-replicator",
    icon = replicator.icon,
    subgroup = "production-machine",
    order = "z[interstellar]-d[replicator]",
    place_result = "quantum-replicator",
    stack_size = 10
  },
  {
    type = "item",
    name = "interstellar-dust-collector",
    icon = dust_collector.icon,
    subgroup = "space-platform",
    order = "z[interstellar]-e[dust-collector]",
    place_result = "interstellar-dust-collector",
    stack_size = 10
  },
  {
    type = "item",
    name = "stellar-fusion-drive",
    icon = fusion_drive.icon,
    subgroup = "space-platform",
    order = "z[interstellar]-f[fusion-drive]",
    place_result = "stellar-fusion-drive",
    stack_size = 10
  },
  {
    type = "item",
    name = "antimatter-drive",
    icon = antimatter_drive.icon,
    subgroup = "space-platform",
    order = "z[interstellar]-g[antimatter-drive]",
    place_result = "antimatter-drive",
    stack_size = 10
  }
})
