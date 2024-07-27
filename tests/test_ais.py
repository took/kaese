import unittest
import re
import importlib.util
from kaese.gameboard.gameboard import GameBoard
from kaese.gameboard.move import Move


class TestAIs(unittest.TestCase):
    def test_make_move(self):
        ai_classes = ["BetterAI", "ClusterAI", "NormalAI", "RandomAI", "SimpleAI", "StupidAI", "TreeAI"]
        for ai_class in ai_classes:
            ai = self.getAi(ai_class)

            # Create a game board
            game_board = GameBoard(size_x=4, size_y=4)

            # Make a move using the AI
            move = ai.get_next_move(gb=game_board, player=1)
            game_board.player_ai[move.player] = move.player_ai

            # Check if the move is valid
            self.assertTrue(isinstance(move, Move))
            self.assertTrue(game_board.is_valid_move(move))
            self.assertEqual(move.player, 1)

            with self.assertRaises(Exception, msg=ai_class) as context:
                ai.get_next_move(gb=game_board, player=2)
            self.assertRegex(str(context.exception), re.compile("wrong player", flags=re.I))

            game_board.make_move(move, print_it=False)

            move = ai.get_next_move(gb=game_board, player=2)
            game_board.player_ai[move.player] = move.player_ai

            # Check if the move is valid
            self.assertTrue(isinstance(move, Move))
            self.assertTrue(game_board.is_valid_move(move))
            self.assertEqual(move.player, 2)

    def test_capture_move(self):
        ai_classes = ["BetterAI", "ClusterAI", "NormalAI", "SimpleAI", "TreeAI"]
        for ai_class in ai_classes:
            ai = self.getAi(ai_class)

            game_board = GameBoard(size_x=4, size_y=4)
            move = Move(1, 0, 1, 1, "Human")
            game_board.make_move(move, False)
            move = Move(1, 1, 1, 2, "Human")
            game_board.make_move(move, False)
            move = Move(0, 1, 0, 1, "Human")
            game_board.make_move(move, False)

            move = ai.get_next_move(gb=game_board, player=2)
            game_board.player_ai[move.player] = move.player_ai

            self.assertTrue(isinstance(move, Move))
            self.assertEqual(move.x, 1)
            self.assertEqual(move.y, 1)
            self.assertEqual(move.horizontal, 0)
            self.assertEqual(move.player, 2)
            self.assertTrue(game_board.is_valid_move(move))

    def test_one_field_cluster_move(self):
        for _ in range(23):
            ai = self.getAi("BetterAI")

            tests = [
                ([  # left and above
                    Move(0, 1, 0, 1, "Human"),
                    Move(1, 0, 1, 2, "Human")
                ], [1, 2], [1, 2]),
                ([  # right and above
                    Move(1, 1, 0, 1, "Human"),
                    Move(1, 0, 1, 2, "Human")
                ], [0, 1], [1, 2]),
                ([  # left and below
                    Move(0, 1, 0, 1, "Human"),
                    Move(1, 1, 1, 2, "Human")
                ], [1, 2], [0, 1]),
                ([  # right and below
                    Move(1, 1, 0, 1, "Human"),
                    Move(1, 1, 1, 2, "Human")
                ], [0, 1], [0, 1]),
                ([  # left and right
                    Move(0, 1, 0, 1, "Human"),
                    Move(1, 1, 0, 2, "Human"),
                ], [1], [0, 1]),
                ([  # above and below
                    Move(1, 0, 1, 1, "Human"),
                    Move(1, 1, 1, 2, "Human")
                ], [0, 1, 2], [0, 1])
            ]

            for moves, x_in, y_in in tests:
                game_board = GameBoard(size_x=3, size_y=3)
                for move in moves:
                    game_board.make_move(move, False)

                move = ai.get_next_move(gb=game_board, player=1)
                self.assertTrue(isinstance(move, Move))
                self.assertIn(move.x, x_in)
                self.assertIn(move.y, y_in)
                self.assertEqual(move.player, 1)
                # self.assertTrue(game_board.is_valid_move(move))

    def test_best_cluster_move(self):
        ai_classes = ["ClusterAI"]
        for ai_class in ai_classes:
            ai = self.getAi(ai_class)

            game_board = GameBoard(size_x=4, size_y=4)
            for move in [
                Move(0, 1, 0, 1, "Human"),
                Move(0, 2, 0, 2, "Human"),
                Move(1, 0, 1, 1, "Human"),
                Move(2, 0, 1, 2, "Human"),
                Move(1, 2, 1, 1, "Human"),
                Move(2, 2, 1, 2, "Human"),
                Move(2, 1, 0, 1, "Human"),
                Move(2, 2, 0, 2, "Human")
            ]:
                game_board.make_move(move, False)

            move = ai.get_next_move(gb=game_board, player=1)
            self.assertIn(move.x, [1, 2])
            self.assertIn(move.y, [1, 2])
            if move.x == 2:
                self.assertEqual(move.y, 1)
                self.assertEqual(move.horizontal, 0)
            if move.y == 2:
                self.assertEqual(move.horizontal, 1)
            self.assertEqual(move.player, 1)

    @staticmethod
    def getAi(ai_class):
        # Import the AI class dynamically
        module_name = f"kaese.ai.{re.sub(r'(?<!^)(?<![A-Z])(?=[A-Z])', '_', ai_class).lower()}"
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            raise ImportError(f"Could not find module: {module_name}")
        ai_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ai_module)
        ai_class = getattr(ai_module, ai_class)

        # Create an instance of the AI
        ai = ai_class()
        return ai


if __name__ == "__main__":
    unittest.main()
