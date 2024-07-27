import unittest
from kaese.gameboard.gameboard import GameBoard
from kaese.savegames.savegames import Savegames


class TestSavegames(unittest.TestCase):
    def test_save_game(self):
        gb = GameBoard()
        filename = "unit-test-empty-12x12.json"
        Savegames.save_game(gb, filename, True)
        self.assertTrue(True)

    def test_load_game(self):
        filename = "./tests/assets/savegames/Empty_Human_vs_Human_12x12.json"
        gb = Savegames.load_game(filename)
        self.assertTrue(isinstance(gb, GameBoard))

    def test_load_game(self):
        filename = "./tests/assets/savegames/Empty_Human_vs_Human_12x12.json"
        gb = Savegames.load_game(filename, True)
        self.assertEqual(gb.player_ai[1], "Human")

    def test_save_overwrite_fail(self):
        gb = GameBoard()
        filename = "unit-test-empty-12x12.json"
        with self.assertRaises(Exception) as context:
            Savegames.save_game(gb, filename, False)

if __name__ == '__main__':
    unittest.main()
