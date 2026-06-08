local C = 299792458
local GUI_ROOT = "interstellar_fleets_root"

local function init_storage()
  storage.fleets = storage.fleets or {}
end

script.on_init(init_storage)
script.on_configuration_changed(init_storage)

local function get_platform_for_player(player)
  if player.surface and player.surface.platform then
    return player.surface.platform
  end
  if player.controller_type == defines.controllers.remote and player.physical_surface and player.physical_surface.platform then
    return player.physical_surface.platform
  end
  return nil
end

local function get_fleet(platform)
  init_storage()
  local key = tostring(platform.index)
  storage.fleets[key] = storage.fleets[key] or {
    size = 1,
    speed_c = 0.01,
    distance_m = 0,
    blueprint_hash = nil,
    auto_boost = false
  }
  if storage.fleets[key].auto_boost == nil then
    storage.fleets[key].auto_boost = false
  end
  return storage.fleets[key]
end

local function count_entities(surface, names)
  local total = 0
  for name, _ in pairs(names) do
    total = total + surface.count_entities_filtered({name = name})
  end
  return total
end

local function completed_research_levels(force, name)
  local technology = force.technologies[name]
  if not technology then
    return 0
  end
  if technology.level and technology.level > 1 then
    return technology.level - 1
  end
  if technology.researched then
    return 1
  end
  return 0
end

local function drive_efficiency_multiplier(force, technology_name, reduction_per_level)
  local levels = completed_research_levels(force, technology_name)
  return math.max(0.2, 1 - levels * reduction_per_level)
end

local function notify(player, message)
  if player and player.valid then
    player.print(message)
  end
end

local function platform_signature(surface, force)
  local parts = {}
  for _, entity in pairs(surface.find_entities_filtered({force = force})) do
    if entity.valid and entity.name ~= "character" and entity.type ~= "resource" and entity.type ~= "item-entity" then
      parts[#parts + 1] = table.concat({
        entity.name,
        math.floor(entity.position.x),
        math.floor(entity.position.y),
        entity.direction or 0
      }, ":")
    end
  end
  table.sort(parts)
  return table.concat(parts, "|")
end

local function insert_to_hub_or_ground(platform, stack)
  local hub = platform.hub
  if hub and hub.valid then
    local inserted = hub.insert(stack)
    local remaining = stack.count - inserted
    if remaining <= 0 then
      return true
    end

    pcall(function()
      hub.surface.spill_item_stack({
        position = hub.position,
        stack = {name = stack.name, count = remaining},
        force = hub.force,
        enable_looted = true
      })
    end)
    return inserted > 0
  end
  return false
end

local function each_platform(callback)
  for _, force in pairs(game.forces) do
    for _, platform in pairs(force.platforms) do
      callback(platform)
    end
  end
end

local function find_platform(platform_index)
  local target = tonumber(platform_index)
  if not target then
    return nil
  end

  local found
  each_platform(function(platform)
    if platform.valid and platform.index == target then
      found = platform
    end
  end)
  return found
end

local function update_caption(player)
  local root = player.gui.screen[GUI_ROOT]
  if not root then
    return
  end
  local platform = get_platform_for_player(player)
  if not platform then
    root.status.caption = {"interstellar-fleets.no-platform"}
    return
  end
  local fleet = get_fleet(platform)
  root.status.caption = {
    "interstellar-fleets.status",
    platform.name,
    fleet.size,
    string.format("%.4f", fleet.speed_c),
    string.format("%.2f", fleet.distance_m / 1000000000)
  }
  if root.interstellar_fleets_auto_boost then
    root.interstellar_fleets_auto_boost.state = fleet.auto_boost
  end
end

local function open_gui(player)
  local root = player.gui.screen[GUI_ROOT]
  if root then
    root.destroy()
    return
  end

  root = player.gui.screen.add({type = "frame", name = GUI_ROOT, direction = "vertical", caption = {"interstellar-fleets.title"}})
  root.auto_center = true
  root.add({type = "label", name = "status", caption = ""})
  local controls = root.add({type = "flow", name = "controls", direction = "horizontal"})
  controls.add({type = "button", name = "interstellar_fleets_merge", caption = {"interstellar-fleets.merge"}})
  controls.add({type = "button", name = "interstellar_fleets_split", caption = {"interstellar-fleets.split"}})
  controls.add({type = "button", name = "interstellar_fleets_update_blueprint", caption = {"interstellar-fleets.update-blueprint"}})
  controls.add({type = "button", name = "interstellar_fleets_boost", caption = {"interstellar-fleets.boost"}})
  root.add({type = "checkbox", name = "interstellar_fleets_auto_boost", caption = {"interstellar-fleets.auto-boost"}, state = false})
  update_caption(player)
end

script.on_event("interstellar-fleets-toggle", function(event)
  local player = game.get_player(event.player_index)
  if player then
    open_gui(player)
  end
end)

script.on_event(defines.events.on_lua_shortcut, function(event)
  if event.prototype_name ~= "interstellar-fleets-toggle" then
    return
  end
  local player = game.get_player(event.player_index)
  if player then
    open_gui(player)
  end
end)

local function clear_progress(surface)
  for _, entity in pairs(surface.find_entities_filtered({type = {"assembling-machine", "furnace", "rocket-silo", "lab"}})) do
    if entity.valid then
      pcall(function()
        entity.crafting_progress = 0
      end)
      pcall(function()
        entity.bonus_progress = 0
      end)
    end
  end
end

local function get_platform_area(surface, force)
  local min_x, min_y, max_x, max_y
  local function include_position(position)
    min_x = math.min(min_x or position.x, position.x)
    min_y = math.min(min_y or position.y, position.y)
    max_x = math.max(max_x or position.x, position.x)
    max_y = math.max(max_y or position.y, position.y)
  end

  for _, entity in pairs(surface.find_entities_filtered({force = force})) do
    if entity.valid and entity.name ~= "character" then
      include_position(entity.position)
    end
  end

  for _, tile in pairs(surface.find_tiles_filtered({name = "space-platform-foundation"})) do
    include_position(tile.position)
  end

  if not min_x then
    return nil
  end

  return {
    {math.floor(min_x) - 4, math.floor(min_y) - 4},
    {math.ceil(max_x) + 4, math.ceil(max_y) + 4}
  }
end

local function clone_platform_layout(source_platform, destination_platform)
  if not source_platform.surface or not destination_platform.surface then
    return false
  end

  local area = get_platform_area(source_platform.surface, source_platform.force)
  if not area then
    return false
  end

  return pcall(function()
    source_platform.surface.clone_area({
      source_area = area,
      destination_area = area,
      destination_surface = destination_platform.surface,
      destination_force = destination_platform.force,
      clone_tiles = true,
      clone_entities = true,
      clear_destination_entities = true,
      clear_destination_decoratives = true,
      expand_map = true,
      create_build_effect_smoke = false
    })
  end)
end

local function merge_fleet(player, platform, fleet)
  local hub = platform.hub
  if not hub or not hub.valid then
    notify(player, {"interstellar-fleets.no-hub"})
    return
  end
  local signature = platform_signature(platform.surface, platform.force)
  if fleet.blueprint_hash and fleet.blueprint_hash ~= signature then
    notify(player, {"interstellar-fleets.blueprint-mismatch"})
    return
  end
  if hub.get_item_count("ship-starter-pack") < 1 then
    notify(player, {"interstellar-fleets.need-pack"})
    return
  end
  fleet.blueprint_hash = signature
  hub.remove_item({name = "ship-starter-pack", count = 1})
  fleet.size = fleet.size + 1
  notify(player, {"interstellar-fleets.merged", fleet.size})
end

local function split_fleet(player, platform, fleet)
  if fleet.size < 2 then
    notify(player, {"interstellar-fleets.cannot-split"})
    return
  end

  local split_size = math.floor(fleet.size / 2)
  fleet.size = fleet.size - split_size
  clear_progress(platform.surface)

  local location = platform.space_location or platform.last_visited_space_location
  local force = player and player.valid and player.force or platform.force
  local ok, new_platform = pcall(function()
    return force.create_space_platform({
      name = platform.name .. " split",
      planet = location and location.name or "nauvis",
      starter_pack = "space-platform-starter-pack"
    })
  end)
  if not ok or not new_platform then
    fleet.size = fleet.size + split_size
    notify(player, {"interstellar-fleets.split-failed"})
    return
  end

  pcall(function()
    new_platform.apply_starter_pack()
  end)
  clone_platform_layout(platform, new_platform)

  local new_fleet = get_fleet(new_platform)
  new_fleet.size = split_size
  new_fleet.speed_c = fleet.speed_c
  new_fleet.distance_m = fleet.distance_m
  new_fleet.blueprint_hash = fleet.blueprint_hash

  notify(player, {"interstellar-fleets.split-complete", fleet.size, split_size})
end

local function boost_fleet(player, platform, fleet, quiet)
  local fusion_drives = count_entities(platform.surface, {["stellar-fusion-drive"] = true})
  local antimatter_drives = count_entities(platform.surface, {["antimatter-drive"] = true})
  local fusion_drive_power = fusion_drives
  local antimatter_drive_power = antimatter_drives * 4
  local drive_power = fusion_drive_power + antimatter_drive_power
  if drive_power == 0 then
    if not quiet then
      notify(player, {"interstellar-fleets.no-drives"})
    end
    return false
  end

  local hub = platform.hub
  if not hub or not hub.valid then
    if not quiet then
      notify(player, {"interstellar-fleets.no-hub"})
    end
    return false
  end

  local gamma = 1 / math.sqrt(math.max(0.0001, 1 - fleet.speed_c * fleet.speed_c))
  local fusion_efficiency = drive_efficiency_multiplier(platform.force, "stellar-fusion-drive-efficiency", 0.08)
  local antimatter_efficiency = drive_efficiency_multiplier(platform.force, "antimatter-drive-efficiency", 0.1)
  local fusion_cell_cost = fusion_drives > 0 and math.max(1, math.ceil(fleet.size * gamma * fusion_drive_power * fusion_efficiency)) or 0
  local antimatter_cost = antimatter_drives > 0 and math.max(1, math.ceil(fleet.size * gamma * antimatter_drives * antimatter_efficiency)) or 0

  if fusion_cell_cost > 0 and hub.get_item_count("fusion-power-cell") < fusion_cell_cost then
    if not quiet then
      notify(player, {"interstellar-fleets.need-fusion-cells", fusion_cell_cost})
    end
    return false
  end

  if antimatter_cost > 0 and hub.get_item_count("antimatter") < antimatter_cost then
    if not quiet then
      notify(player, {"interstellar-fleets.need-antimatter", antimatter_cost})
    end
    return false
  end

  if fusion_cell_cost > 0 then
    hub.remove_item({name = "fusion-power-cell", count = fusion_cell_cost})
  end
  if antimatter_cost > 0 then
    hub.remove_item({name = "antimatter", count = antimatter_cost})
  end

  local acceleration = drive_power * 0.00005 / gamma
  fleet.speed_c = math.min(0.999, fleet.speed_c + acceleration)
  if not quiet then
    notify(player, {"interstellar-fleets.boosted", string.format("%.4f", fleet.speed_c), fusion_cell_cost, antimatter_cost})
  end
  return true
end

local function update_fleet_blueprint(player, platform, fleet)
  fleet.blueprint_hash = platform_signature(platform.surface, platform.force)
  clear_progress(platform.surface)
  notify(player, {"interstellar-fleets.blueprint-updated"})
end

script.on_event(defines.events.on_gui_click, function(event)
  local element = event.element
  if not element or not element.valid then
    return
  end

  local player = game.get_player(event.player_index)
  if not player then
    return
  end

  if element.name == "interstellar_fleets_merge" or element.name == "interstellar_fleets_split" or element.name == "interstellar_fleets_update_blueprint" or element.name == "interstellar_fleets_boost" then
    local platform = get_platform_for_player(player)
    if not platform then
      player.print({"interstellar-fleets.no-platform"})
      return
    end

    local fleet = get_fleet(platform)
    if element.name == "interstellar_fleets_merge" then
      merge_fleet(player, platform, fleet)
    elseif element.name == "interstellar_fleets_split" then
      split_fleet(player, platform, fleet)
    elseif element.name == "interstellar_fleets_update_blueprint" then
      update_fleet_blueprint(player, platform, fleet)
    elseif element.name == "interstellar_fleets_boost" then
      boost_fleet(player, platform, fleet)
    end
    update_caption(player)
  end
end)

script.on_event(defines.events.on_gui_checked_state_changed, function(event)
  local element = event.element
  if not element or not element.valid or element.name ~= "interstellar_fleets_auto_boost" then
    return
  end

  local player = game.get_player(event.player_index)
  if not player then
    return
  end

  local platform = get_platform_for_player(player)
  if not platform then
    player.print({"interstellar-fleets.no-platform"})
    element.state = false
    return
  end

  local fleet = get_fleet(platform)
  fleet.auto_boost = element.state
  player.print(fleet.auto_boost and {"interstellar-fleets.auto-boost-enabled"} or {"interstellar-fleets.auto-boost-disabled"})
  update_caption(player)
end)

script.on_nth_tick(60, function()
  init_storage()

  each_platform(function(platform)
    if platform.valid and platform.surface and platform.surface.valid then
      local fleet = get_fleet(platform)
      local surface = platform.surface
      local speed_bonus = math.max(0, fleet.size - 1)

      if speed_bonus > 0 then
        surface.global_effect = {
          speed = speed_bonus,
          consumption = speed_bonus
        }
      else
        surface.global_effect = nil
      end

      local collectors = count_entities(surface, {["interstellar-dust-collector"] = true})
      if collectors > 0 then
        local dust = math.floor(math.max(1, collectors * fleet.size * fleet.speed_c * 25))
        insert_to_hub_or_ground(platform, {name = "interstellar-dust", count = dust})
      end

      if fleet.auto_boost then
        boost_fleet(nil, platform, fleet, true)
      end

      local drives = count_entities(surface, {["stellar-fusion-drive"] = true, ["antimatter-drive"] = true})
      if drives > 0 then
        fleet.distance_m = fleet.distance_m + fleet.speed_c * C
      end
    end
  end)

  for _, player in pairs(game.connected_players) do
    update_caption(player)
  end
end)

remote.add_interface("interstellar-fleets", {
  get_fleet = function(platform_index)
    local platform = find_platform(platform_index)
    if not platform then
      return nil
    end

    local fleet = get_fleet(platform)
    return {
      size = fleet.size,
      speed_c = fleet.speed_c,
      distance_m = fleet.distance_m,
      blueprint_hash = fleet.blueprint_hash,
      auto_boost = fleet.auto_boost
    }
  end,
  merge = function(player_index, platform_index)
    local player = player_index and game.get_player(player_index) or nil
    local platform = find_platform(platform_index)
    if not platform then
      return false
    end
    merge_fleet(player, platform, get_fleet(platform))
    return true
  end,
  split = function(player_index, platform_index)
    local player = player_index and game.get_player(player_index) or nil
    local platform = find_platform(platform_index)
    if not platform then
      return false
    end
    split_fleet(player, platform, get_fleet(platform))
    return true
  end,
  update_blueprint = function(player_index, platform_index)
    local player = player_index and game.get_player(player_index) or nil
    local platform = find_platform(platform_index)
    if not platform then
      return false
    end
    update_fleet_blueprint(player, platform, get_fleet(platform))
    return true
  end,
  boost = function(player_index, platform_index)
    local player = player_index and game.get_player(player_index) or nil
    local platform = find_platform(platform_index)
    if not platform then
      return false
    end
    boost_fleet(player, platform, get_fleet(platform))
    return true
  end,
  set_auto_boost = function(platform_index, enabled)
    local platform = find_platform(platform_index)
    if not platform then
      return false
    end
    get_fleet(platform).auto_boost = enabled and true or false
    return true
  end
})
