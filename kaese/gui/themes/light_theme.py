from kaese.gui.themes.theme import Theme


class LightTheme(Theme):
    """
    Implement default theme.
    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_name():
        return "Light"
