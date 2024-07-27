from typing import Callable

import pygame

from kaese.gui.button import Button
from kaese.gui.themes.theme import Theme


class PopupWindow:
    """PopupWindow object"""

    theme: Theme
    screen: pygame.surface
    text_message: str
    font_size_message: int
    text_button: str
    font_size_button: int
    font_name: str
    callback_function: Callable[[], None]
    color_set: str

    window_padding_width: int
    window_padding_height: int
    border_width: int

    rect: pygame.rect
    dismiss_button: Button

    def __init__(
            self,
            theme: Theme,
            screen: pygame.surface,
            text_message: str,
            font_size_message: int = 17,
            text_button: str = "Dismiss",
            font_size_button: int = 27,
            font_name: str = "Arial",
            callback_function: Callable[[], None] = None,
            color_set: str = "default"
    ) -> None:
        self.theme = theme
        self.screen = screen

        self.text_message = text_message
        self.font_size_message = font_size_message
        self.text_button = text_button
        self.font_size_button = font_size_button
        self.font_name = font_name
        self.callback_function = callback_function
        self.color_set = color_set

        # Set window and border size
        self.window_padding_width = 50
        self.window_padding_height = 150
        self.border_width = 8

        # Init Dismiss Button
        self.dismiss_button = Button(
            self.theme,
            self.screen,
            0,
            0,
            120,
            35,
            self.text_button,
            self.font_size_button,
            self.font_name,
            self.callback_dismiss_button
        )

    def draw(self) -> None:
        # Be sure, pygame.font.init() has already been called in your project before!

        # Set colors
        if self.color_set == "player_1":
            border_color = self.theme.popup_window_color_set_player_1_border_color
            background_color = self.theme.popup_window_color_set_player_1_background_color
            font_color = self.theme.popup_window_color_set_player_1_font_color
        elif self.color_set == "player_2":
            border_color = self.theme.popup_window_color_set_player_2_border_color
            background_color = self.theme.popup_window_color_set_player_2_background_color
            font_color = self.theme.popup_window_color_set_player_2_font_color
        elif self.color_set == "draw":
            border_color = self.theme.popup_window_color_set_draw_border_color
            background_color = self.theme.popup_window_color_set_draw_background_color
            font_color = self.theme.popup_window_color_set_draw_font_color
        else:
            # default
            border_color = self.theme.popup_window_color_set_default_border_color
            background_color = self.theme.popup_window_color_set_default_background_color
            font_color = self.theme.popup_window_color_set_default_font_color

        # Set size of PopupWindow depending on screen size
        # TODO Dynamically choose font_size and window_padding from width of text_message
        # TODO Choose x and y depending on position in PopupWindowsQueue, enforce max width and non-centered positioning
        # TODO Maybe even support detection of text height using intelligent line break (with enforced width?)?
        self.rect = pygame.Rect(
            self.window_padding_width,
            self.window_padding_height,
            self.screen.get_width() - (2 * self.window_padding_width),
            self.screen.get_height() - (2 * self.window_padding_height)
        )

        # Update position of Dismiss-Button in case of a resize event has occurred
        self.dismiss_button.rect.x = self.rect.x + self.rect.width - self.border_width - 120 - 30
        self.dismiss_button.rect.y = self.rect.y + self.rect.height - self.border_width - 35 - 30

        # Draw border, background, text and button
        pygame.draw.rect(self.screen, border_color, self.rect)

        pygame.draw.rect(self.screen, background_color, (
            self.rect.x + self.border_width,
            self.rect.y + self.border_width,
            self.rect.width - (2 * self.border_width),
            self.rect.height - (2 * self.border_width)
        ))

        font_obj = pygame.font.SysFont(self.font_name, self.font_size_message)
        text_message_surface = font_obj.render(self.text_message, True, font_color)
        text_message_x = self.rect.centerx - (text_message_surface.get_width() // 2)
        text_message_y = (self.rect.centery - 35 - 30 - 5) - (text_message_surface.get_height() // 2)
        self.screen.blit(text_message_surface, (text_message_x, text_message_y))

        self.dismiss_button.draw()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle event for Dismiss button. Return True, if redraw is needed."""
        redraw = False
        if self.dismiss_button.handle_event(event):
            redraw = True
        return redraw

    def callback_dismiss_button(self) -> None:
        """Close Popup"""
        if self.callback_function:
            self.callback_function()
