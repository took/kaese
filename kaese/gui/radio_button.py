from typing import Callable

import pygame

from kaese.gui.button import Button
from kaese.gui.themes.theme import Theme


class RadioButton(Button):
    """RadioButton object"""

    radius: int
    player_color: pygame.Color

    is_selected: bool

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
            radius: int,
            player_color: pygame.color,
            text: str,
            font_size: int,
            font_name: str,
            callback_function: Callable[[str], None]
    ) -> None:
        super().__init__(theme, screen, x, y, width, height, text, font_size, font_name, callback_function)
        self.radius = radius
        self.player_color = player_color

        self.is_selected = False

        self.is_mouseover = False
        self.is_pressed = False

    def draw(self) -> None:
        # Be sure, pygame.font.init() has already been called in your project before!
        font_obj = pygame.font.SysFont(self.theme.gui_font_name, self.font_size)

        font_color = self.theme.radio_button_font_color
        button_color = self.theme.button_body_color
        if self.is_mouseover:
            button_color = self.theme.button_body_mouseover_color
        if self.is_pressed:
            button_color = self.theme.button_body_pressed_color

        circle_center_x = self.rect.x + self.radius + 10
        circle_center_y = self.rect.centery
        pygame.draw.circle(self.screen, button_color, (circle_center_x, circle_center_y), self.radius - 1)
        pygame.draw.circle(self.screen, (0, 0, 0), (circle_center_x, circle_center_y), self.radius, 2)
        if self.is_selected:
            pygame.draw.circle(self.screen, self.player_color, (circle_center_x, circle_center_y), self.radius // 2)

        text_surface = font_obj.render(self.text, True, font_color)
        text_x = circle_center_x + self.radius + 10
        text_y = circle_center_y - (text_surface.get_height() // 2)
        self.screen.blit(text_surface, (text_x, text_y))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle event for radio button. Return True, if redraw is needed."""

        redraw = False
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
                self.callback_function(self.text)  # TODO Fix false positive warning "Unexpected argument"
                redraw = True
            if self.is_pressed:
                redraw = True
            self.is_pressed = False
        return redraw
