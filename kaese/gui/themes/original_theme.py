import pygame

from kaese.gui.themes.theme import Theme


class OriginalTheme(Theme):
    """
    Implement theme with historical colors from 2023.
    """
    def __init__(self):
        super().__init__(
            button_body_color=pygame.Color("#969696"),
            button_body_inactive_color=pygame.Color("#aaaaaa"),
            button_body_mouseover_color=pygame.Color("#787878"),
            button_body_pressed_color=pygame.Color("#5a5a5a"),
            button_border_color=pygame.Color("#646464"),
            button_border_inactive_color=pygame.Color("#8c8c8c"),
            button_font_color=pygame.Color("#171717"),
            button_font_inactive_color=pygame.Color("#5a5a5a"),

            gui_background_color=pygame.Color("#c8c8c8"),
            gui_font_color=pygame.Color("#000000"),
            gui_font_name="Arial",
            gui_player_1_color=pygame.Color("#ff0000"),
            gui_player_2_color=pygame.Color("#00ff00"),

            playing_surface_background_color=pygame.Color("#bebebe"),
            playing_surface_border_color=pygame.Color("#0000ff"),
            playing_surface_box_background_color=pygame.Color("#ffffff"),
            playing_surface_line_default_color=pygame.Color("#aaaaaa"),
            playing_surface_line_player_1_color=pygame.Color("#d70000"),
            playing_surface_line_player_2_color=pygame.Color("#00d700"),
            playing_surface_line_player_1_last_move_color=pygame.Color("#820000"),
            playing_surface_line_player_2_last_move_color=pygame.Color("#005000"),

            popup_new_game_background_color=pygame.Color("#fafafa"),
            popup_new_game_border_color=pygame.Color("#323232"),

            popup_window_color_set_player_1_border_color=pygame.Color("#b4172a"),
            popup_window_color_set_player_1_background_color=pygame.Color("#f2dfe2"),
            popup_window_color_set_player_1_font_color=pygame.Color("#000000"),

            popup_window_color_set_player_2_border_color=pygame.Color("#17b42a"),
            popup_window_color_set_player_2_background_color=pygame.Color("#dfeff2"),
            popup_window_color_set_player_2_font_color=pygame.Color("#000000"),

            popup_window_color_set_draw_border_color=pygame.Color("#ffeb3b"),
            popup_window_color_set_draw_background_color=pygame.Color("#fff59d"),
            popup_window_color_set_draw_font_color=pygame.Color("#000000"),

            popup_window_color_set_default_border_color=pygame.Color("#969696"),
            popup_window_color_set_default_background_color=pygame.Color("#b4b4b4"),
            popup_window_color_set_default_font_color=pygame.Color("#000000"),

            radio_button_font_color=pygame.Color("#000000"),

            text_box_font_color=pygame.Color("#000000"),
            text_box_border_color=pygame.Color("#000000"),
            text_box_background_color=pygame.Color("#ffffff"),
        )
    @staticmethod
    def get_name():
        return "Original"
