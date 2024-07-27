class Move:
    """Dumb container for a move (holds coordinates of a line and player)"""
    x: int = 0
    y: int = 0
    horizontal: int = 0  # horizontal=0 represents a vertical line, horizontal=1 represents a horizontal line
    player: int = 0
    player_ai: str = ""

    def __init__(self, x: int, y: int, horizontal: int, player: int = 0, player_ai: str = ""):
        self.x = x
        self.y = y
        self.horizontal = horizontal
        self.player = player
        self.player_ai = player_ai
