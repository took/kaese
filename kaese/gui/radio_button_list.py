from typing import List, Optional, Callable

import pygame

from kaese.gui.radio_button import RadioButton
from kaese.gui.themes.theme import Theme


class RadioButtonList:
    """RadioButtonList object"""

    theme: Theme
    screen: pygame.surface
    x: int
    y: int
    width: int
    entry_height: int
    radius: int
    distance: int
    player_color: pygame.color
    text: str
    font_size: int
    font_name: str
    callback_function: Callable[[], None]

    buttons: List[RadioButton]

    selected_option: Optional[str]

    is_mouseover: bool
    is_pressed: bool

    def __init__(
            self,
            theme: Theme,
            screen: pygame.surface,
            x: int,
            y: int,
            width: int,
            entry_height: int,
            distance: int,
            radius: int,
            player_color: pygame.color,
            selected_option: str,
            options: List[str],
            font_size: int,
            font_name: str,
            callback_function: Callable[[], None]
    ) -> None:
        self.theme = theme
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.entry_height = entry_height
        self.radius = radius
        self.distance = distance
        self.player_color = player_color
        self.selected_option = selected_option
        self.options = options
        self.font_size = font_size
        self.font_name = font_name
        self.callback_function = callback_function

        self.buttons = []
        for i, option in enumerate(self.options):
            button = RadioButton(
                self.theme,
                self.screen,
                self.x,
                self.y + (i * (self.entry_height + self.distance)),
                self.width,
                self.entry_height,
                self.radius,
                self.player_color,
                option,
                self.font_size,
                self.font_name,
                self.callback_radio_button
            )
            if self.selected_option == option:
                button.is_selected = True
            self.buttons.append(button)

        self.selected_option = None

        self.is_mouseover = False
        self.is_pressed = False

    def draw(self) -> None:
        for button in self.buttons:
            button.rect.x = self.x  # TODO This is a very very dirty update
            button.draw()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle event for all radio buttons. Return True, if redraw is needed."""

        redraw = False
        for button in self.buttons:
            if button.handle_event(event):
                redraw = True
        return redraw

    def callback_radio_button(self, text: str) -> None:
        for button in self.buttons:
            if button.text == text:
                button.is_selected = True
                self.selected_option = button.text
            else:
                button.is_selected = False
        self.callback_function()
