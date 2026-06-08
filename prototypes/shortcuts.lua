data:extend({
  {
    type = "custom-input",
    name = "interstellar-fleets-toggle",
    key_sequence = "SHIFT + I",
    consuming = "none"
  },
  {
    type = "shortcut",
    name = "interstellar-fleets-toggle",
    action = "lua",
    associated_control_input = "interstellar-fleets-toggle",
    toggleable = false,
    icon = "__interstellar-fleets__/graphics/icons/ship-starter-pack.png",
    icon_size = 64,
    small_icon = "__interstellar-fleets__/graphics/icons/ship-starter-pack.png",
    small_icon_size = 64
  }
})
