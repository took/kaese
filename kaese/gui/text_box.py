import pygame

from kaese.gui.themes.theme import Theme


class TextBox:
    """Draw a rectangle with nice looking border in which text can be placed"""

    theme: Theme
    screen: pygame.surface
    x: int
    y: int
    width: int
    height: int
    border_width: int
    text_left: str
    text_right: str
    font_size: int
    font_name: str
    font_color: pygame.color
    border_color: pygame.color
    backgrund_color: pygame.color

    def __init__(
            self,
            theme: Theme,
            screen: pygame.surface,
            x: int,
            y: int,
            width: int = 47,
            height: int = 30,
            border_width: int = 3,
            text_left: str = "",
            text_right: str = "",
            font_size: int = 28,
            font_name: str = None,
            font_color: pygame.color = None,
            border_color: pygame.color = None,
            background_color: pygame.color = None
    ) -> None:
        self.theme = theme
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border_width = border_width
        self.text_left = text_left
        self.text_right = text_right
        self.font_size = font_size
        self.font_name = font_name if font_name else self.theme.gui_font_name
        self.font_color = font_color if font_color else self.theme.text_box_font_color
        self.border_color = border_color if border_color else self.theme.text_box_border_color
        self.backgrund_color = background_color if background_color else self.theme.text_box_background_color

    def draw(self) -> None:
        # Be sure, pygame.font.init() has already been called in your project before!
        font_obj = pygame.font.SysFont(self.font_name, self.font_size)
        pygame.draw.rect(
            self.screen,
            self.border_color,
            (self.x, self.y, self.width, self.height),
            border_radius=self.border_width
        )
        pygame.draw.rect(
            self.screen,
            self.backgrund_color,
            (
                self.x + self.border_width,
                self.y + self.border_width,
                self.width - (2 * self.border_width),
                self.height - (2 * self.border_width)
            )
        )
        if self.text_left:
            text_surface = font_obj.render(self.text_left, True, self.font_color)
            self.screen.blit(
                text_surface,
                (
                    self.x + self.border_width + 5,
                    self.y + self.border_width + 5,
                )
            )
        if self.text_right:
            text_surface = font_obj.render(self.text_right, True, self.font_color)
            self.screen.blit(
                text_surface,
                (
                    self.x + self.width - self.border_width - text_surface.get_width() - 5,
                    self.y + self.border_width + 5,
                )
            )
