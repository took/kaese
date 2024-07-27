from kaese.network.messages.Message import Message


class NewGameMsg(Message):
    def __init__(self, game_name: str, size_x: int, size_y: int, player_1: str = 'Client_1', player_2: str = 'Client_2',
                 load_filename: str = ''):
        self.message_type = 'NewGameMsg'
        self.game_name = game_name
        self.size_x = max(2, min(30, size_x))
        self.size_y = max(2, min(30, size_y))
        self.player_1 = player_1
        self.player_2 = player_2
        self.load_filename = load_filename
