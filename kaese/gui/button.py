from typing import Callable

import pygame

from kaese.gui.themes.theme import Theme


class Button:
    """Button object"""

    theme: Theme
    screen: pygame.surface
    rect: pygame.rect
    text: str
    font_size: int
    font_name: str
    callback_function: Callable[[], None]
    render_button_inactive: bool
    is_mouseover: bool
    is_pressed: bool

    def __init__(
            self,
            theme: Theme,
            screen: pygame.surface,
            x: int,
            y: int,
            width: int,
            height: int,
            text: str,
            font_size: int,
            font_name: str,
            callback_function: Callable[[], None],
            render_button_inactive: bool = False
    ) -> None:
        self.theme = theme
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.font_name = font_name
        self.callback_function = callback_function
        self.render_button_inactive = render_button_inactive

        self.is_mouseover = False
        self.is_pressed = False

    def draw(self) -> None:
        # Be sure, pygame.font.init() has already been called in your project before!
        font_obj = pygame.font.SysFont(self.font_name, self.font_size)

        border_width = 3
        font_color = self.theme.button_font_color
        border_color = self.theme.button_border_color
        body_color = self.theme.button_body_color
        if self.render_button_inactive:
            font_color = self.theme.button_font_inactive_color
            border_color = self.theme.button_border_inactive_color
            body_color = self.theme.button_body_inactive_color
        else:
            if self.is_mouseover:
                body_color = self.theme.button_body_mouseover_color
            if self.is_pressed:
                body_color = self.theme.button_body_pressed_color

        pygame.draw.rect(self.screen, border_color, self.rect, border_radius=5)
        pygame.draw.rect(self.screen, body_color, (
            self.rect.x + border_width,
            self.rect.y + border_width,
            self.rect.width - (2 * border_width),
            self.rect.height - (2 * border_width)
        ))

        text_surface = font_obj.render(self.text, True, font_color)

        text_x = self.rect.centerx - (text_surface.get_width() // 2)
        text_y = self.rect.centery - (text_surface.get_height() // 2)
        self.screen.blit(text_surface, (text_x, text_y))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle event for button. Return True, if redraw is needed."""

        redraw = False
        if self.render_button_inactive:
            return redraw
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if not self.is_mouseover:
                    redraw = True
                self.is_mouseover = True
            else:
                if self.is_mouseover:
                    redraw = True
                self.is_mouseover = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if not self.is_pressed:
                    redraw = True
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.callback_function()
                redraw = True
            if self.is_pressed:
                redraw = True
            self.is_pressed = False
        return redraw
