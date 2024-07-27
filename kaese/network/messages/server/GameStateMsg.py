import hashlib

from kaese.gameboard.gameboard import GameBoard
from kaese.network.messages.Message import Message


class GameStateMsg(Message):
    def __init__(self, for_player: int, game_name: str, gb: GameBoard = None):
        self.message_type = 'GameStateMsg'
        self.for_player = for_player
        self.game_name = game_name

        if gb is not None:
            self.size_x = gb.size_x
            self.size_y = gb.size_y
            boxes = []
            for x in range(self.size_x):
                column = []
                for y in range(self.size_y):
                    column.append((gb.boxes[x][y].owner, gb.boxes[x][y].line_right, gb.boxes[x][y].line_below))
                boxes.append(column)
            self.boxes = boxes
            self.current_player = gb.current_player
            if for_player == 1:
                self.player_ai_1 = 'You'
                self.player_ai_2 = 'Remote'
            else:
                self.player_ai_1 = 'Remote'
                self.player_ai_2 = 'You'
            self.winner = gb.winner
            self.win_counter_1 = gb.win_counter[1]
            self.win_counter_2 = gb.win_counter[2]
            self.moves_made = gb.moves_made
            self.remaining_moves = gb.remaining_moves
            # self.last_move = Optional[Move]  # last move, stored to highlight that line in some way in the GUI
            # self.move_history = List[Move]
            self.move_history_pointer = gb.move_history_pointer
            hash_me = '-'.join([
                game_name,
                str(gb.size_x),
                str(gb.size_y),
                '_'.join([
                        ';'.join([
                                ','.join([
                                    str(box.owner),
                                    str(box.line_right),
                                    str(box.line_below)
                                ]) for box in row
                            ]) for row in gb.boxes
                    ]),
                str(gb.current_player)
            ])
            self.gameboard_hash = hashlib.sha1(hash_me.encode()).hexdigest()
