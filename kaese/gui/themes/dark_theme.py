import pygame

from kaese.gui.themes.theme import Theme


class DarkTheme(Theme):
    def __init__(self):
        super().__init__(
            button_body_color=pygame.Color("#333333"),
            button_body_inactive_color=pygame.Color("#444444"),
            button_body_mouseover_color=pygame.Color("#555555"),
            button_body_pressed_color=pygame.Color("#666666"),
            button_border_color=pygame.Color("#777777"),
            button_border_inactive_color=pygame.Color("#888888"),
            button_font_color=pygame.Color("#CCCCCC"),
            button_font_inactive_color=pygame.Color("#888888"),

            gui_background_color=pygame.Color("#121212"),
            gui_font_color=pygame.Color("#CCCCCC"),
            gui_font_name="Arial",
            gui_player_1_color=pygame.Color("#FF4444"),
            gui_player_2_color=pygame.Color("#44FF44"),

            playing_surface_background_color=pygame.Color("#1E1E1E"),
            playing_surface_border_color=pygame.Color("#0077FF"),
            playing_surface_box_background_color=pygame.Color("#333333"),
            playing_surface_line_default_color=pygame.Color("#555555"),
            playing_surface_line_player_1_color=pygame.Color("#FF3333"),
            playing_surface_line_player_2_color=pygame.Color("#33FF33"),
            playing_surface_line_player_1_last_move_color=pygame.Color("#990000"),
            playing_surface_line_player_2_last_move_color=pygame.Color("#009900"),

            popup_new_game_background_color=pygame.Color("#1F1F1F"),
            popup_new_game_border_color=pygame.Color("#666666"),

            popup_window_color_set_player_1_border_color=pygame.Color("#FF3355"),
            popup_window_color_set_player_1_background_color=pygame.Color("#442222"),
            popup_window_color_set_player_1_font_color=pygame.Color("#CCCCCC"),

            popup_window_color_set_player_2_border_color=pygame.Color("#33FF55"),
            popup_window_color_set_player_2_background_color=pygame.Color("#224422"),
            popup_window_color_set_player_2_font_color=pygame.Color("#CCCCCC"),

            popup_window_color_set_draw_border_color=pygame.Color("#FFD700"),
            popup_window_color_set_draw_background_color=pygame.Color("#887700"),
            popup_window_color_set_draw_font_color=pygame.Color("#000000"),

            popup_window_color_set_default_border_color=pygame.Color("#777777"),
            popup_window_color_set_default_background_color=pygame.Color("#444444"),
            popup_window_color_set_default_font_color=pygame.Color("#CCCCCC"),

            radio_button_font_color=pygame.Color("#CCCCCC"),

            text_box_font_color=pygame.Color("#CCCCCC"),
            text_box_border_color=pygame.Color("#CCCCCC"),
            text_box_background_color=pygame.Color("#111111"),
        )

    @staticmethod
    def get_name():
        return "Dark"
