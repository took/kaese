from kaese.gui.gui_exception import GuiException
from kaese.gui.themes.light_theme import LightTheme
from kaese.gui.themes.dark_theme import DarkTheme
from kaese.gui.themes.original_theme import OriginalTheme


class ThemesManager:
    """Themes Manager class"""

    def __init__(self):
        """
        Initialize a Theme instance.
        """
        pass

    @staticmethod
    def get_available_themes():
        return ['Light', 'Dark', 'Original']

    @staticmethod
    def get_theme(theme: str):
        if theme == "Light":
            return LightTheme()
        if theme == "Dark":
            return DarkTheme()
        if theme == "Original":
            return OriginalTheme()
        raise GuiException("Theme '%s' not found." % theme)
