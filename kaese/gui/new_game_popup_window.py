from typing import Callable

import pygame

from kaese.gui.button import Button
from kaese.gui.popup_window import PopupWindow
from kaese.gui.text_box import TextBox
from kaese.gui.themes.theme import Theme


class NewGamePopupWindow(PopupWindow):
    """PopupWindow object"""

    theme: Theme
    screen: pygame.surface
    gameboard_x: int
    gameboard_y: int
    callback_function_cancel: Callable[[], None]
    callback_function_ok: Callable[[], None]

    text_message: str
    font_size_message: int
    text_ok_button: str
    text_cancel_button: str
    font_size_button: int
    font_name: str

    window_padding_width: int
    window_padding_height: int
    border_width: int

    rect: pygame.rect
    plus_x_button: Button
    minus_x_button: Button
    plus_y_button: Button
    minus_y_button: Button
    ok_button: Button
    cancel_button: Button

    def __init__(
            self,
            theme: Theme,
            screen: pygame.surface,
            gameboard_x: int,
            gameboard_y: int,
            callback_function_cancel: Callable[[], None] = None,
            callback_function_ok: Callable[[], None] = None,
    ) -> None:
        self.theme = theme
        self.screen = screen
        self.gameboard_x = gameboard_x
        self.gameboard_y = gameboard_y
        self.callback_function_cancel = callback_function_cancel
        self.callback_function_ok = callback_function_ok

        self.text_message = "Select field size!"
        self.font_size_message = 14
        self.text_ok_button = "New Game"
        self.text_cancel_button = "Cancel"
        self.font_size_button = 18
        self.font_size_textbox = 12

        # Set window and border size
        self.window_padding_width = 50
        self.window_padding_height = 150
        self.border_width = 8

        # Init Buttons
        self.plus_x_button = Button(
            self.theme,
            self.screen,
            0,
            0,
            18,
            18,
            "+",
            17,
            self.theme.gui_font_name,
            self.callback_plus_x_button
        )
        self.minus_x_button = Button(
            self.theme,
            self.screen,
            0,
            0,
            18,
            18,
            "-",
            17,
            self.theme.gui_font_name,
            self.callback_minus_x_button
        )
        self.plus_y_button = Button(
            self.theme,
            self.screen,
            0,
            0,
            18,
            18,
            "+",
            17,
            self.theme.gui_font_name,
            self.callback_plus_y_button
        )
        self.minus_y_button = Button(
            self.theme,
            self.screen,
            0,
            0,
            18,
            18,
            "-",
            17,
            self.theme.gui_font_name,
            self.callback_minus_y_button
        )
        self.ok_button = Button(
            self.theme,
            self.screen,
            0,
            0,
            110,
            28,
            self.text_ok_button,
            self.font_size_button,
            self.theme.gui_font_name,
            self.callback_ok_button
        )
        self.cancel_button = Button(
            self.theme,
            self.screen,
            0,
            0,
            80,
            28,
            self.text_cancel_button,
            self.font_size_button,
            self.theme.gui_font_name,
            self.callback_cancel_button
        )

    def draw(self) -> None:
        # Be sure, pygame.font.init() has already been called in your project before!

        # Set size of PopupWindow depending on screen size
        self.rect = pygame.Rect(
            self.window_padding_width,
            self.window_padding_height // 2,
            max(360, self.screen.get_width() // 2),
            self.screen.get_height() // 2
        )

        # Update position of Buttons in case of a resize event has occurred
        self.plus_x_button.rect.x = self.rect.x + 110
        self.plus_x_button.rect.y = self.rect.y + 117

        self.minus_x_button.rect.x = self.rect.x + 110
        self.minus_x_button.rect.y = self.rect.y + 137

        self.plus_y_button.rect.x = self.rect.x + 210
        self.plus_y_button.rect.y = self.rect.y + 117

        self.minus_y_button.rect.x = self.rect.x + 210
        self.minus_y_button.rect.y = self.rect.y + 137

        self.ok_button.rect.x = self.rect.x + self.rect.width - self.border_width - 110 - 30
        self.ok_button.rect.y = self.rect.y + self.rect.height - self.border_width - 28 - 30

        self.cancel_button.rect.x = self.rect.x + self.border_width + 30
        self.cancel_button.rect.y = self.rect.y + self.rect.height - self.border_width - 28 - 30

        # Draw border, background, text, x and y size and buttons
        pygame.draw.rect(self.screen, self.theme.popup_new_game_border_color, self.rect)

        pygame.draw.rect(self.screen, self.theme.popup_new_game_background_color, (
            self.rect.x + self.border_width,
            self.rect.y + self.border_width,
            self.rect.width - (2 * self.border_width),
            self.rect.height - (2 * self.border_width)
        ))

        font_obj = pygame.font.SysFont(self.theme.gui_font_name, self.font_size_message)
        text_message_surface = font_obj.render(self.text_message, True, self.theme.gui_font_color)
        text_message_x = self.rect.centerx - (text_message_surface.get_width() // 2)
        text_message_y = (self.rect.y + 40) - (text_message_surface.get_height() // 2)
        self.screen.blit(text_message_surface, (text_message_x, text_message_y))

        TextBox(
            self.theme,
            self.screen,
            self.rect.x + 60,
            self.rect.y + 120,
            text_left="%d" % self.gameboard_x,
            font_size=self.font_size_textbox
        ).draw()
        TextBox(
            self.theme,
            self.screen,
            self.rect.x + 160,
            self.rect.y + 120,
            text_left="%d" % self.gameboard_y,
            font_size=self.font_size_textbox
        ).draw()

        self.plus_x_button.draw()
        self.minus_x_button.draw()
        self.plus_y_button.draw()
        self.minus_y_button.draw()
        self.cancel_button.draw()
        self.ok_button.draw()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle event for Dismiss button. Return True, if redraw is needed."""
        redraw = False
        if self.plus_x_button.handle_event(event):
            redraw = True
        if self.minus_x_button.handle_event(event):
            redraw = True
        if self.plus_y_button.handle_event(event):
            redraw = True
        if self.minus_y_button.handle_event(event):
            redraw = True
        if self.ok_button.handle_event(event):
            redraw = True
        if self.cancel_button.handle_event(event):
            redraw = True
        return redraw

    def callback_plus_x_button(self) -> None:
        """Increase gameboard_x"""
        self.gameboard_x = min(50, self.gameboard_x + 1)

    def callback_minus_x_button(self) -> None:
        """Decrease gameboard_x"""
        self.gameboard_x = max(3, self.gameboard_x - 1)

    def callback_plus_y_button(self) -> None:
        """Increase gameboard_y"""
        self.gameboard_y = min(50, self.gameboard_y + 1)

    def callback_minus_y_button(self) -> None:
        """Decrease gameboard_y"""
        self.gameboard_y = max(3, self.gameboard_y - 1)

    def callback_ok_button(self) -> None:
        """Close Popup and init new game"""
        if self.callback_function_ok:
            self.callback_function_ok()

    def callback_cancel_button(self) -> None:
        """Close Popup"""
        if self.callback_function_cancel:
            self.callback_function_cancel()
