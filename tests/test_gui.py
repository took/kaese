import unittest

import pygame

from kaese.gameboard.gameboard import GameBoard
from kaese.gui.button import Button
# from tests.mockup.gui import Gui
from kaese.gui.gui import Gui
from kaese.gui.playing_surface import PlayingSurface
from kaese.gui.popup_windows_queue import PopupWindowsQueue
from kaese.gui.radio_button_list import RadioButtonList
from kaese.gui.text_box import TextBox
from kaese.gui.themes.themes_manager import ThemesManager
from kaese.savegames.savegames import Savegames


class TestGui(unittest.TestCase):
    def test_button(self):
        button = Button(
            theme=ThemesManager.get_theme("Dark"),
            screen=pygame.Surface(size=(500, 500)),
            x=5,
            y=5,
            width=100,
            height=30,
            text="Test",
            font_size=11,
            font_name="Arial",
            callback_function=self.callback
        )
        self.assertTrue(isinstance(button, Button))

    def test_playing_surface(self):
        theme = ThemesManager.get_theme("Dark")
        ps = PlayingSurface(
            gui=Gui(
                theme=theme,
                gb_size_x=5,
                gb_size_y=5,
            ),
            theme=theme
        )
        self.assertTrue(isinstance(ps, PlayingSurface))

    def test_popup_windows_queue(self):
        pwq = PopupWindowsQueue()
        self.assertTrue(isinstance(pwq, PopupWindowsQueue))

    def test_radio_button_list(self):
        rbl = RadioButtonList(
            theme=ThemesManager.get_theme("Dark"),
            screen=pygame.Surface(size=(500, 500)),
            x=5,
            y=5,
            width=100,
            entry_height=10,
            distance=5,
            radius=5,
            player_color=(255, 0, 0),
            selected_option="selected",
            options=["selected", "option2", "option3"],
            font_size=11,
            font_name="Arial",
            callback_function=self.callback
        )
        self.assertTrue(isinstance(rbl, RadioButtonList))

    def test_text_box(self):
        tb = TextBox(
            theme=ThemesManager.get_theme("Dark"),
            screen=pygame.Surface(size=(500, 500)),
            x=5,
            y=5,
            width=100,
            height=30
        )
        self.assertTrue(isinstance(tb, TextBox))

    def callback(self):
        pass


if __name__ == '__main__':
    unittest.main()
