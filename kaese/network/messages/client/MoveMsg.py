from kaese.network.messages.Message import Message


class MoveMsg(Message):
    game_name: str
    gameboard_hash: str
    x: int = 0
    y: int = 0
    horizontal: int = 0  # horizontal=0 represents a vertical line, horizontal=1 represents a horizontal line

    def __init__(self, game_name: str, gameboard_hash: str, x: int, y: int, horizontal: int):
        self.message_type = 'MoveMsg'
        self.game_name = game_name
        self.gameboard_hash = gameboard_hash
        self.x = x
        self.y = y
        self.horizontal = horizontal
