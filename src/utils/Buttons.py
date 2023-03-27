def change_toggle_button_style(bit, button, style_off, style_on):
    button.setProperty('class', (style_on if bit else style_off))
    button.style().unpolish(button)
    button.style().polish(button)