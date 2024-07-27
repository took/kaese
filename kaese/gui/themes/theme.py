from abc import ABC

import pygame


class Theme(ABC):
    """
    Abstract Theme class. The default values defined here will be used with default theme "Light".
    """

    def __init__(
            self,
            button_body_color: pygame.Color = pygame.Color("#969696"),
            button_body_inactive_color: pygame.Color = pygame.Color("#aaaaaa"),
            button_body_mouseover_color: pygame.Color = pygame.Color("#787878"),
            button_body_pressed_color: pygame.Color = pygame.Color("#5a5a5a"),
            button_border_color: pygame.Color = pygame.Color("#646464"),
            button_border_inactive_color: pygame.Color = pygame.Color("#8c8c8c"),
            button_font_color: pygame.Color = pygame.Color("#171717"),
            button_font_inactive_color: pygame.Color = pygame.Color("#5a5a5a"),

            gui_background_color: pygame.Color = pygame.Color("#c8c8c8"),
            gui_font_color: pygame.Color = pygame.Color("#000000"),
            gui_font_name: str = "Arial",
            gui_player_1_color: pygame.Color = pygame.Color("#ff0000"),
            gui_player_2_color: pygame.Color = pygame.Color("#00ff00"),

            playing_surface_background_color: pygame.Color = pygame.Color("#bebebe"),
            playing_surface_border_color: pygame.Color = pygame.Color("#0000ff"),
            playing_surface_box_background_color: pygame.Color = pygame.Color("#ffffff"),
            playing_surface_line_default_color: pygame.Color = pygame.Color("#aaaaaa"),
            playing_surface_line_player_1_color: pygame.Color = pygame.Color("#d70000"),
            playing_surface_line_player_2_color: pygame.Color = pygame.Color("#00d700"),
            playing_surface_line_player_1_last_move_color: pygame.Color = pygame.Color("#820000"),
            playing_surface_line_player_2_last_move_color: pygame.Color = pygame.Color("#005000"),

            popup_new_game_background_color: pygame.Color = pygame.Color("#fafafa"),
            popup_new_game_border_color: pygame.Color = pygame.Color("#323232"),

            popup_window_color_set_player_1_border_color: pygame.Color = pygame.Color("#b4172a"),
            popup_window_color_set_player_1_background_color: pygame.Color = pygame.Color("#f2dfe2"),
            popup_window_color_set_player_1_font_color: pygame.Color = pygame.Color("#000000"),

            popup_window_color_set_player_2_border_color: pygame.Color = pygame.Color("#17b42a"),
            popup_window_color_set_player_2_background_color: pygame.Color = pygame.Color("#dfeff2"),
            popup_window_color_set_player_2_font_color: pygame.Color = pygame.Color("#000000"),

            popup_window_color_set_draw_border_color: pygame.Color = pygame.Color("#ffeb3b"),
            popup_window_color_set_draw_background_color: pygame.Color = pygame.Color("#fff59d"),
            popup_window_color_set_draw_font_color: pygame.Color = pygame.Color("#000000"),

            popup_window_color_set_default_border_color: pygame.Color = pygame.Color("#969696"),
            popup_window_color_set_default_background_color: pygame.Color = pygame.Color("#b4b4b4"),
            popup_window_color_set_default_font_color: pygame.Color = pygame.Color("#000000"),

            radio_button_font_color: pygame.Color = pygame.Color("#000000"),

            text_box_font_color: pygame.Color = pygame.Color("#000000"),
            text_box_border_color: pygame.Color = pygame.Color("#000000"),
            text_box_background_color: pygame.Color = pygame.Color("#ffffff"),
    ):
        """
        Initialize a Theme instance.
        """
        self.button_body_color = button_body_color
        self.button_body_inactive_color = button_body_inactive_color
        self.button_body_mouseover_color = button_body_mouseover_color
        self.button_body_pressed_color = button_body_pressed_color
        self.button_border_color = button_border_color
        self.button_border_inactive_color = button_border_inactive_color
        self.button_font_color = button_font_color
        self.button_font_inactive_color = button_font_inactive_color

        self.gui_background_color = gui_background_color
        self.gui_font_color = gui_font_color
        self.gui_font_name = gui_font_name
        self.gui_player_1_color = gui_player_1_color
        self.gui_player_2_color = gui_player_2_color

        self.playing_surface_background_color = playing_surface_background_color
        self.playing_surface_border_color = playing_surface_border_color
        self.playing_surface_box_background_color = playing_surface_box_background_color
        self.playing_surface_line_default_color = playing_surface_line_default_color
        self.playing_surface_line_player_1_color = playing_surface_line_player_1_color
        self.playing_surface_line_player_2_color = playing_surface_line_player_2_color
        self.playing_surface_line_player_1_last_move_color = playing_surface_line_player_1_last_move_color
        self.playing_surface_line_player_2_last_move_color = playing_surface_line_player_2_last_move_color

        self.popup_new_game_background_color = popup_new_game_background_color
        self.popup_new_game_border_color = popup_new_game_border_color

        self.popup_window_color_set_player_1_border_color = popup_window_color_set_player_1_border_color
        self.popup_window_color_set_player_1_background_color = popup_window_color_set_player_1_background_color
        self.popup_window_color_set_player_1_font_color = popup_window_color_set_player_1_font_color

        self.popup_window_color_set_player_2_border_color = popup_window_color_set_player_2_border_color
        self.popup_window_color_set_player_2_background_color = popup_window_color_set_player_2_background_color
        self.popup_window_color_set_player_2_font_color = popup_window_color_set_player_2_font_color

        self.popup_window_color_set_draw_border_color = popup_window_color_set_draw_border_color
        self.popup_window_color_set_draw_background_color = popup_window_color_set_draw_background_color
        self.popup_window_color_set_draw_font_color = popup_window_color_set_draw_font_color

        self.popup_window_color_set_default_border_color = popup_window_color_set_default_border_color
        self.popup_window_color_set_default_background_color = popup_window_color_set_default_background_color
        self.popup_window_color_set_default_font_color = popup_window_color_set_default_font_color

        self.radio_button_font_color = radio_button_font_color

        self.text_box_font_color = text_box_font_color
        self.text_box_border_color = text_box_border_color
        self.text_box_background_color = text_box_background_color

    @staticmethod
    def get_name():
        return "Default"
