-- Runs only in the isolated test mod directory created by smoke_test.py.
local function check(value, message)
  assert(value, "Interstellar Fleets regression: " .. message)
end

local function near(actual, expected, message)
  check(math.abs(actual - expected) < 0.00001, message .. ": " .. tostring(actual))
end

script.on_init(function()
  local force = game.forces.player
  local platform = force.create_space_platform({
    name = "Regression fleet", planet = "nauvis",
    starter_pack = {name = "space-platform-starter-pack", quality = "legendary"}
  })
  platform.apply_starter_pack()
  check(platform.hub and platform.hub.valid, "starter hub is valid")
  storage.platform = platform
  local tiles = {}
  for x = -20, 20 do
    for y = -20, 20 do
      tiles[#tiles + 1] = {name = "space-platform-foundation", position = {x, y}}
    end
  end
  platform.surface.set_tiles(tiles)
  force.technologies["orbital-industry"].researched = true
  storage.machines = {}
  for _, definition in ipairs({
    {"interstellar-foundry", "metallurgic-science-pack", {-10, -10}},
    {"interstellar-electromagnetic-plant", "electromagnetic-science-pack", {10, -10}},
    {"interstellar-biochamber", "agricultural-science-pack", {-10, 10}},
    {"interstellar-cryogenic-plant", "cryogenic-science-pack", {10, 10}}
  }) do
    local recipe = "interstellar-" .. definition[2]
    check(force.recipes[recipe].enabled, "orbital science unlocked: " .. recipe)
    local machine = platform.surface.create_entity({name = definition[1], position = definition[3], force = force})
    check(machine and machine.valid, "orbital machine builds: " .. definition[1])
    machine.set_recipe(recipe)
    check(machine.get_module_inventory().insert({name = "speed-module-3", count = 1}) == 1, "test module inserts")
    check(machine.get_recipe() and machine.get_recipe().name == recipe, "orbital science recipe accepted: " .. recipe)
    storage.machines[#storage.machines + 1] = machine
  end
  storage.cargo_bay = platform.surface.create_entity({name = "cargo-bay", position = {0, 12}, force = force})
  storage.belt = platform.surface.create_entity({name = "transport-belt", position = {5, 12}, force = force})
  check(storage.cargo_bay and storage.belt, "cargo bay and belt build")
  platform.surface.global_effect = {speed = 0.3, consumption = 0.4, productivity = 0.2}
  platform.hub.insert({name = "ship-starter-pack", count = 1})
  check(remote.call("interstellar-fleets", "merge", nil, platform.index), "merge succeeds")
  check(remote.call("interstellar-fleets", "get_fleet", platform.index).size == 2, "merged size is two")
  check(not remote.call("interstellar-fleets", "merge", nil, platform.index), "missing pack returns false")
end)

script.on_event(defines.events.on_tick, function(event)
  local platform = storage.platform
  if event.tick == 61 then
    local effects = platform.surface.global_effect
    near(effects.speed, 1.3, "fleet speed preserves preexisting bonus")
    near(effects.consumption, 1.4, "fleet energy preserves preexisting bonus")
    near(effects.productivity, 0.2, "fleet preserves productivity")
    check(remote.call("interstellar-fleets", "split", nil, platform.index), "real clone/split succeeds")
    check(remote.call("interstellar-fleets", "get_fleet", platform.index).size == 1, "source size is one")
    local split
    for _, candidate in pairs(platform.force.platforms) do
      if candidate.index ~= platform.index then split = candidate end
    end
    check(split and split.valid and split.hub and split.hub.valid, "split hub survives clone_area")
    check(split.hub.quality.name == platform.hub.quality.name, "split preserves actual hub quality")
    check(remote.call("interstellar-fleets", "get_fleet", split.index).size == 1, "destination size is one")
    check(not remote.call("interstellar-fleets", "split", nil, platform.index), "singleton split returns false")
    for _, machine in ipairs(storage.machines) do
      local cloned = split.surface.find_entity(machine.name, machine.position)
      check(cloned and cloned.valid, "machine survives split: " .. machine.name)
      check(cloned.get_recipe().name == machine.get_recipe().name, "recipe survives split: " .. machine.name)
      check(cloned.get_module_inventory().get_item_count("speed-module-3") == 1, "module survives split")
    end
    check(split.surface.find_entity("cargo-bay", storage.cargo_bay.position), "cargo bay survives split")
    check(split.surface.find_entity("transport-belt", storage.belt.position), "belt survives split")
    storage.split = split
  elseif event.tick == 121 then
    local effects = platform.surface.global_effect
    near(effects.speed, 0.3, "split removes only fleet speed")
    near(effects.consumption, 0.4, "split removes only fleet energy")
    near(effects.productivity, 0.2, "split keeps productivity")
    check(storage.split.valid and storage.split.hub.valid, "split platform remains valid")
    log("INTERSTELLAR_FLEETS_RUNTIME_TESTS_PASSED")
  end
end)
