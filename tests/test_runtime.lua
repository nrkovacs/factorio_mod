-- Offline regressions against the real control.lua. Run from the repository root
-- with Lua 5.2+: lua tests/test_runtime.lua [alternate-control.lua]
local control_path = (arg and arg[1]) or "control.lua"
local passed, failed = 0, 0
local function equal(actual, expected, description)
  assert(actual == expected, (description or "value") .. ": expected " .. tostring(expected) .. ", got " .. tostring(actual))
end
local function near(actual, expected)
  assert(math.abs(actual - expected) < 1e-9, "expected " .. expected .. ", got " .. tostring(actual))
end
local function copy(value)
  if type(value) ~= "table" then return value end
  local result = {}
  for key, item in pairs(value) do result[key] = copy(item) end
  return result
end
local function setup(options)
  options = options or {}
  local world = {events = {}, platforms = {}, players = {}, next_index = 1}
  local env = setmetatable({}, {__index = _G})
  env.log = function() end
  env.storage = {}
  env.defines = {controllers = {remote = 1}, events = {}}
  for _, name in ipairs({"on_force_created", "on_space_platform_changed_state", "on_lua_shortcut", "on_gui_click", "on_gui_checked_state_changed", "on_forces_merged", "on_force_reset"}) do
    env.defines.events[name] = name
  end
  env.script = {
    on_init = function(callback) world.init = callback end,
    on_configuration_changed = function(callback) world.configuration_changed = callback end,
    on_event = function(event, callback) world.events[event] = callback end,
    on_nth_tick = function(_, callback) world.tick = callback end
  }
  env.remote = {add_interface = function(_, interface) world.api = interface end}
  local force = {name = "player", technologies = {
    ['interstellar-fleets'] = {enabled = false, researched = false},
    ['quantum-replication'] = {enabled = false, researched = false}
  }, players = {}, platforms = {}}
  force.unlock_space_location = function() force.location_unlocked = true end
  force.lock_space_location = function() force.location_unlocked = false end
  world.force = force
  env.game = {forces = {player = force}, connected_players = {}, print = function() end,
    get_player = function(index) return world.players[index] end}
  function world.add_platform(owner)
    owner = owner or force
    local platform = {index = world.next_index, name = "Test fleet", valid = true, force = owner,
      space_location = {name = "nauvis"}}
    world.next_index = world.next_index + 1
    local inventory = {['ship-starter-pack'] = 10, ['fusion-power-cell'] = 10000}
    local hub = {valid = true, name = "space-platform-hub", type = "space-platform-hub",
      position = {x = 0, y = 0}, direction = 0, quality = {name = "normal"}}
    hub.copy_settings = function() end
    hub.get_item_count = function(name) return inventory[name] or 0 end
    hub.remove_item = function(stack)
      local removed = math.min(stack.count, inventory[stack.name] or 0)
      inventory[stack.name] = (inventory[stack.name] or 0) - removed
      return removed
    end
    hub.insert = function(stack)
      local inserted = math.min(stack.count, platform.capacity or math.huge)
      inventory[stack.name] = (inventory[stack.name] or 0) + inserted
      return inserted
    end
    platform.inventory, platform.hub = inventory, hub
    local state = {effect = nil, writes = 0}
    local surface = {valid = true, platform = platform, entities = {hub},
      tiles = {{name = "space-platform-foundation", position = {x = 0, y = 0}}}, counts = {}}
    setmetatable(surface, {
      __index = function(_, key) if key == "global_effect" then return copy(state.effect) end end,
      __newindex = function(self, key, value)
        if key == "global_effect" then state.effect, state.writes = copy(value), state.writes + 1
        else rawset(self, key, value) end
      end
    })
    surface.count_entities_filtered = function(filter) return surface.counts[filter.name] or 0 end
    surface.find_entities_filtered = function(filter)
      local result = {}
      for _, entity in pairs(surface.entities) do
        local include = not filter.type
        if type(filter.type) == "table" then
          for _, kind in pairs(filter.type) do if kind == entity.type then include = true end end
        elseif filter.type then include = filter.type == entity.type end
        if include then result[#result + 1] = entity end
      end
      return result
    end
    surface.find_tiles_filtered = function() return surface.tiles end
    surface.clone_area = function(settings)
      if options.clone_error then error("injected clone failure") end
      local destination = settings.destination_surface
      destination.tiles = copy(surface.tiles)
      if settings.clone_entities then
        destination.entities = copy(surface.entities)
        destination.platform.hub = destination.entities[1]
      end
    end
    surface.clone_entities = function(settings)
      local destination = settings.destination_surface
      for _, entity in ipairs(settings.entities) do
        assert(entity.type ~= "space-platform-hub", "hubs cannot be cloned")
        destination.entities[#destination.entities + 1] = copy(entity)
      end
      if options.clone_partial then table.remove(destination.entities) end
    end
    platform.surface, platform.effect_state = surface, state
    platform.destroy = function()
      platform.destroyed = true
      platform.valid, surface.valid = false, false
    end
    platform.apply_starter_pack = function()
      if options.starter_error then error("injected starter pack failure") end
      if options.starter_no_hub then platform.hub = nil; return nil end
      return hub
    end
    owner.platforms[#owner.platforms + 1] = platform
    world.platforms[#world.platforms + 1] = platform
    return platform
  end
  force.create_space_platform = function(settings)
    if options.create_error then error("injected create failure") end
    if options.create_nil then return nil end
    world.created = world.add_platform(force)
    if type(settings.starter_pack) == "table" then
      world.created.hub.quality = {name = settings.starter_pack.quality}
    end
    return world.created
  end
  world.source = world.add_platform()
  world.machine = {valid = true, name = "assembling-machine-3", type = "assembling-machine",
    position = {x = 2.5, y = 0.5}, direction = 0, quality = {name = "normal"}, crafting_progress = 0.75, bonus_progress = 0.5}
  table.insert(world.source.surface.entities, world.machine)
  world.env = env
  assert(loadfile(control_path, "t", env))()
  world.init()
  world.api.get_fleet(world.source.index)
  world.fleet = env.storage.fleets[tostring(world.source.index)]
  return world
end
local function test(name, run)
  local ok, error_message = pcall(run)
  if ok then passed = passed + 1; print("PASS " .. name)
  else failed = failed + 1; print("FAIL " .. name .. ": " .. tostring(error_message)) end
end

test("dust throughput is not capped by backlog capacity", function()
  local w = setup()
  w.source.surface.counts['interstellar-dust-collector'] = 120000
  w.tick()
  equal(w.source.inventory['interstellar-dust'], 30000)
  equal(w.fleet.dust_backlog, 0)
end)
test("dust overflow is bounded and drains", function()
  local w = setup()
  w.source.capacity = 0
  w.source.surface.counts['interstellar-dust-collector'] = 120000
  w.tick()
  equal(w.fleet.dust_backlog, 20000)
  w.source.surface.counts['interstellar-dust-collector'] = 0
  w.source.capacity = 100000
  w.tick()
  equal(w.source.inventory['interstellar-dust'], 20000)
  equal(w.fleet.dust_backlog, 0)
end)
test("fleet effect preserves unrelated effects", function()
  local w = setup()
  w.source.surface.global_effect = {speed = 0.25, consumption = -0.2, productivity = 0.5, pollution = 0.3, quality = 0.1}
  w.fleet.size = 2
  w.tick()
  near(w.source.surface.global_effect.speed, 1.25)
  near(w.source.surface.global_effect.consumption, 0.8)
  equal(w.source.surface.global_effect.productivity, 0.5)
  equal(w.source.surface.global_effect.pollution, 0.3)
  equal(w.source.surface.global_effect.quality, 0.1)
end)
test("fleet effect removal preserves outside changes", function()
  local w = setup()
  w.fleet.size = 2
  w.tick()
  w.source.surface.global_effect = {speed = 1.75, consumption = 1.5, productivity = 0.5}
  w.fleet.size = 1
  w.tick()
  near(w.source.surface.global_effect.speed, 0.75)
  near(w.source.surface.global_effect.consumption, 0.5)
  equal(w.source.surface.global_effect.productivity, 0.5)
end)
test("unmodified singleton and unchanged fleets do not rewrite effects", function()
  local w = setup()
  w.tick()
  equal(w.source.effect_state.writes, 0)
  w.fleet.size = 2
  w.tick()
  equal(w.source.effect_state.writes, 1)
  w.tick()
  equal(w.source.effect_state.writes, 1)
end)
test("effect float readback does not lose a percentage point", function()
  local w = setup()
  w.fleet.size = 2
  w.tick()
  w.source.surface.global_effect = {speed = 1.299999952, consumption = 1.399999976}
  w.fleet.size = 1
  w.tick()
  near(w.source.surface.global_effect.speed, 0.3)
  near(w.source.surface.global_effect.consumption, 0.4)
end)
for _, failure in ipairs({"create_error", "create_nil", "starter_error", "starter_no_hub", "clone_error", "clone_partial"}) do
  test("split rollback: " .. failure, function()
    local w = setup({[failure] = true})
    w.fleet.size = 5
    local result = w.api.split(nil, w.source.index)
    equal(w.fleet.size, 5, "source fleet size")
    equal(w.machine.crafting_progress, 0.75, "source crafting progress")
    equal(w.machine.bonus_progress, 0.5, "source bonus progress")
    equal(result, false, "remote failure result")
    if w.created then
      equal(w.created.destroyed, true, "failed destination removed")
      equal(w.env.storage.fleets[tostring(w.created.index)], nil, "failed destination storage")
    end
  end)
end
test("successful split commits sizes and clears both progress copies", function()
  local w = setup()
  w.fleet.size, w.fleet.speed_c, w.fleet.distance_m = 5, 0.25, 9876
  equal(w.api.split(nil, w.source.index), true)
  equal(w.fleet.size, 3)
  local split = w.env.storage.fleets[tostring(w.created.index)]
  equal(split.size, 2)
  equal(split.speed_c, 0.25)
  equal(split.distance_m, 9876)
  equal(w.machine.crafting_progress, 0)
  equal(w.created.surface.entities[2].crafting_progress, 0)
end)
test("split always uses the source force", function()
  local w = setup()
  w.fleet.size = 2
  local other = {name = "other"}
  other.create_space_platform = function() error("wrong force was used") end
  w.players[1] = {valid = true, force = other, print = function() end}
  equal(w.api.split(1, w.source.index), true)
  equal(w.created.force, w.source.force)
end)
test("split preserves hub quality and does not clone transient entities", function()
  local w = setup()
  w.fleet.size = 2
  w.source.hub.quality = {name = "legendary"}
  table.insert(w.source.surface.entities, {valid = true, name = "cargo-pod", type = "cargo-pod", position = {x = 0, y = 0}})
  equal(w.api.split(nil, w.source.index), true)
  equal(w.created.hub.quality.name, "legendary")
  equal(#w.created.surface.entities, 2)
end)
test("merge reports missing pack", function()
  local w = setup()
  w.source.inventory['ship-starter-pack'] = 0
  equal(w.api.merge(nil, w.source.index), false)
  equal(w.fleet.size, 1)
end)
test("boost reports missing drives and fuel", function()
  local w = setup()
  equal(w.api.boost(nil, w.source.index), false)
  w.source.surface.counts['stellar-fusion-drive'] = 1
  w.source.inventory['fusion-power-cell'] = 0
  equal(w.api.boost(nil, w.source.index), false)
end)
test("successful merge and boost return true", function()
  local w = setup()
  equal(w.api.merge(nil, w.source.index), true)
  equal(w.fleet.size, 2)
  w.source.surface.counts['stellar-fusion-drive'] = 1
  equal(w.api.boost(nil, w.source.index), true)
  assert(w.fleet.speed_c > 0.01)
end)
test("signature detects quality replacement", function()
  local w = setup()
  w.api.merge(nil, w.source.index)
  w.machine.quality = {name = "legendary"}
  equal(w.api.merge(nil, w.source.index), false)
  equal(w.fleet.size, 2)
end)
test("signature detects sub-tile position changes", function()
  local w = setup()
  w.api.merge(nil, w.source.index)
  w.machine.position.x = 2.75
  equal(w.api.merge(nil, w.source.index), false)
end)
test("signature detects foundation changes", function()
  local w = setup()
  w.api.merge(nil, w.source.index)
  table.insert(w.source.surface.tiles, {name = "space-platform-foundation", position = {x = 8, y = 3}})
  equal(w.api.merge(nil, w.source.index), false)
end)
test("signature ignores transient entities", function()
  local w = setup()
  w.api.merge(nil, w.source.index)
  table.insert(w.source.surface.entities, {valid = true, name = "cargo-pod", type = "cargo-pod"})
  equal(w.api.merge(nil, w.source.index), true)
end)
test("legacy signatures require an explicit blueprint refresh", function()
  local w = setup()
  w.fleet.size = 2
  w.fleet.blueprint_hash = "assembling-machine-3:2:0:0|space-platform-hub:0:0:0"
  equal(w.api.merge(nil, w.source.index), false)
  equal(w.api.update_blueprint(nil, w.source.index), true)
  equal(w.api.merge(nil, w.source.index), true)
end)
test("a recreated force name can unlock the gate normally", function()
  local w = setup()
  w.env.storage.shattered_reached.player = true
  w.events.on_force_created({force = w.force})
  equal(w.env.storage.shattered_reached.player, nil)
  equal(w.force.technologies['interstellar-fleets'].enabled, false)
  equal(w.force.location_unlocked, false)
  w.source.space_location = {name = "shattered-planet"}
  w.events.on_space_platform_changed_state({platform = w.source})
  equal(w.env.storage.shattered_reached.player, true)
  equal(w.force.technologies['interstellar-fleets'].researched, true)
  equal(w.force.technologies['quantum-replication'].enabled, true)
  equal(w.force.location_unlocked, true)
end)
test("force merge transfers source progress before clearing its name", function()
  local w = setup()
  w.env.storage.shattered_reached.retired = true
  w.events.on_forces_merged({source_name = "retired", destination = w.force})
  equal(w.env.storage.shattered_reached.retired, nil)
  equal(w.env.storage.shattered_reached.player, true)
  equal(w.force.technologies['interstellar-fleets'].researched, true)
  equal(w.force.technologies['quantum-replication'].enabled, true)
  equal(w.force.location_unlocked, true)
end)
test("force merge preserves destination and inherited research progress", function()
  local w = setup()
  w.env.storage.shattered_reached.player = true
  w.events.on_forces_merged({source_name = "retired", destination = w.force})
  equal(w.env.storage.shattered_reached.player, true)
  w.env.storage.shattered_reached.player = nil
  w.force.technologies['quantum-replication'].researched = true
  w.events.on_forces_merged({source_name = "other", destination = w.force})
  equal(w.env.storage.shattered_reached.player, true)
  equal(w.force.location_unlocked, true)
end)
print(string.format("Runtime regressions: %d passed, %d failed", passed, failed))
assert(failed == 0, "runtime regression failures")
