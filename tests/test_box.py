import unittest
from kaese.gameboard.box import Box


class TestBox(unittest.TestCase):
    def test_box_initialization(self):
        box1 = Box()
        self.assertIsInstance(box1, Box)
        self.assertEqual(box1.owner, 0)
        self.assertEqual(box1.line_right, 0)
        self.assertEqual(box1.line_below, 0)

        box2 = Box(owner=1, line_right=2, line_below=1)
        self.assertEqual(box2.owner, 1)
        self.assertEqual(box2.line_right, 2)
        self.assertEqual(box2.line_below, 1)


if __name__ == '__main__':
    unittest.main()
