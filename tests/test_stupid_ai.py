import unittest
from kaese.ai.stupid_ai import StupidAI
from kaese.gameboard.gameboard import GameBoard
from kaese.gameboard.move import Move


class TestStupidAI(unittest.TestCase):
    def test_make_move(self):
        # Create a game board
        game_board = GameBoard(size_x=4, size_y=4)

        # Create an instance of StupidAI
        ai = StupidAI()

        # Make a move using the StupidAI
        move = ai.get_next_move(gb=game_board, player=1)
        game_board.player_ai[move.player] = move.player_ai

        # Check if the move is valid
        self.assertTrue(isinstance(move, Move))
        self.assertTrue(game_board.is_valid_move(move))


if __name__ == '__main__':
    unittest.main()
