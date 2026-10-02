-- Generated Blender atlases use a fixed origin in every frame. The manifest is
-- written by the asset packer alongside the PNGs; shifts are measured in tiles.
local manifest = require("prototypes.art-manifest")
local art = {}
local root = "__interstellar-fleets__/graphics/"
local directions = {"north", "east", "south", "west"}

local function sprite(name, layer, direction, idle)
  local spec = assert(manifest[name], "Missing art metadata for " .. name)
  local animation = {
    filename = root .. "entity/" .. name .. "/" .. name .. "-" .. layer .. ".png",
    priority = "high",
    width = spec.width,
    height = spec.height,
    frame_count = idle and 1 or spec.frame_count,
    line_length = spec.line_length,
    animation_speed = spec.animation_speed or 0.15,
    scale = spec.scale,
    shift = table.deepcopy(spec.shift),
    y = (direction - 1) * spec.height * math.ceil(spec.frame_count / spec.line_length)
  }
  if layer == "glow" then
    animation.draw_as_glow = true
    animation.blend_mode = "additive"
  elseif layer == "shadow" then
    animation.draw_as_shadow = true
  end
  return animation
end

local function layers(name, direction, glow, idle)
  local result = {
    sprite(name, "animation", direction, idle),
    sprite(name, "shadow", direction, idle)
  }
  if glow then
    result[#result + 1] = sprite(name, "glow", direction, idle)
  end
  return {layers = result}
end

local function animation_4way(name, glow)
  if manifest[name].directions == 1 then
    return layers(name, 1, glow)
  end
  local result = {}
  for index, direction in ipairs(directions) do
    result[direction] = layers(name, index, glow)
  end
  return result
end

local function glow_visualisation(name)
  local result = {fadeout = true}
  if manifest[name].directions == 1 then
    result.animation = sprite(name, "glow", 1)
  else
    for index, direction in ipairs(directions) do
      result[direction .. "_animation"] = sprite(name, "glow", index)
    end
  end
  return result
end

local function prepare_working_sound(sound)
  if type(sound) ~= "table" then return end
  -- Space Age's electromagnetic plant has separate warm-up, rotation and
  -- cool-down loops. The custom art has one working cycle, so retain only its
  -- steady rotation loop instead of playing all three transitions together.
  for _, main in ipairs(sound.main_sounds or {}) do
    for _, visual in ipairs(main.play_for_working_visualisations or {}) do
      if visual == "rotation" then
        sound.main_sounds = {main}
        break
      end
    end
    if #sound.main_sounds == 1 then break end
  end
  -- Vanilla accents refer to frames in much longer animation cycles. Preserve
  -- the loop sounds, but remove their obsolete visual gates and frame accents.
  -- WorkingSound itself can inherit the MainSound visual-gate property, so this
  -- cleanup also covers that form and nested main_sounds entries.
  sound.sound_accents = nil
  sound.play_for_working_visualisations = nil
  for _, child in pairs(sound) do
    prepare_working_sound(child)
  end
end

local function apply_common(prototype)
  assert(manifest[prototype.name], "Missing art metadata for " .. prototype.name)
  prototype.icon = nil
  prototype.icon_size = nil
  prototype.icons = {{icon = root .. "icons/" .. prototype.name .. ".png", icon_size = 64}}
  prototype.water_reflection = nil
  prototype.factoriopedia_simulation = nil
  prepare_working_sound(prototype.working_sound)
end

local function connected_visualisations(prototype)
  local names = {}
  local function collect(value)
    if type(value) ~= "table" then return end
    for _, name in ipairs(value.enable_working_visualisations or {}) do
      names[name] = true
    end
    for _, child in pairs(value) do collect(child) end
  end
  collect(prototype.fluid_boxes)
  collect(prototype.fuel_fluid_box)
  collect(prototype.oxidizer_fluid_box)
  local result = {}
  for _, visual in ipairs((prototype.graphics_set or {}).working_visualisations or {}) do
    if visual.name and names[visual.name] then
      -- Native socket overlays remain aligned with the unchanged fluid ports.
      -- Their animation cycles are independent of the new machine body.
      result[#result + 1] = table.deepcopy(visual)
    end
  end
  result[#result + 1] = glow_visualisation(prototype.name)
  return result
end

function art.apply_lab(prototype)
  apply_common(prototype)
  prototype.on_animation = layers(prototype.name, 1, true)
  prototype.off_animation = layers(prototype.name, 1, false, true)
end

function art.apply_crafting_machine(prototype)
  apply_common(prototype)
  local source = prototype.graphics_set or {}
  prototype.graphics_set = {
    animation = animation_4way(prototype.name, false),
    working_visualisations = connected_visualisations(prototype),
    circuit_connector_layer = source.circuit_connector_layer,
    circuit_connector_secondary_draw_order = source.circuit_connector_secondary_draw_order
  }
  -- A source machine's mirrored graphics must never bring its old body back.
  -- Fluid-box mirroring and all connection locations remain inherited.
  prototype.graphics_set_flipped = nil
end

function art.apply_collector(prototype)
  apply_common(prototype)
  local source = prototype.graphics_set
  prototype.graphics_set = {
    animation = animation_4way(prototype.name, true),
    -- Factorio articulates these independently while collecting real chunks.
    arm_head_animation = source.arm_head_animation,
    arm_head_top_animation = source.arm_head_top_animation,
    arm_link = source.arm_link
  }
end

function art.apply_drive(prototype)
  apply_common(prototype)
  -- Drives are item-fueled structures, not native fluid-burning thrusters.
  -- SimpleEntityWithOwnerPrototype uses AnimationVariations ("animations"),
  -- and has no graphics_set or activity-dependent exhaust shader.
  prototype.animations = layers(prototype.name, 1, true)
end

return art
