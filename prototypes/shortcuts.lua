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
    icon = "__space-age__/graphics/icons/space-platform-hub.png",
    small_icon = "__space-age__/graphics/icons/space-platform-hub.png"
  }
})
