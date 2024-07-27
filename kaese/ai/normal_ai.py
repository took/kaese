from typing import Optional, List
import random
import logging
from kaese.ai.ai import AI
from kaese.ai.ai_exception import AIException
from kaese.ai.random_ai import RandomAI
from kaese.ai.simple_ai import SimpleAI
from kaese.gameboard.move import Move
from kaese.gameboard.gameboard import GameBoard


class NormalAI(AI):
    """
    SimpleAI class represents an AI player that looks for boxes that can be closed right now. If none found,
    it tries to find boxes that have less than 2 lines around them to prevent a closeable field for the opponent.
    In that case, if possible, it prefers boxes where another line is close by to build up clusters.

    If none of the above is possible, it selects a random valid move.

    It inherits from the AI class.
    """

    def get_next_move(self, gb: GameBoard, player: int) -> Move:
        """
        Calculates and returns the next move for the AI player.

        Args:
            gb (GameBoard): The game board object.
            player (int): The AI player's identifier.

        Returns:
            Optional[Move]: The next valid move found on the game board, or None if no moves are available.
        """
        player_ai = self.__class__.__name__

        if gb.current_player != player:
            raise AIException("NormalAI: Wrong Player, can not handle this...")

        # Check if any fields can be captured immediately and return the first found move
        capture_field_move = SimpleAI.get_capture_field_move(gb, player, player_ai)
        if capture_field_move:
            return capture_field_move

        # before using "any valid move" search for moves where umrandungen<2
        capture_field_move = NormalAI.get_close_to_other_lines_move(gb, player, player_ai)
        if capture_field_move:
            return capture_field_move

        # Fallback: Use a random valid move
        logging.info("%s: Using fallback (a random valid move)" % player_ai)
        return RandomAI.get_random_valid_move(gb, player, player_ai)

    @staticmethod
    def get_field_with_count_of_surroundings(gb: GameBoard) -> List[List[int]]:
        """calculate how many surroundings every field has and return 2-dim list with integers 0-4"""
        # TODO tests schreiben
        surroundings = []
        for x in range(0, gb.size_x):
            row = []
            for y in range(0, gb.size_y):
                row.append(gb.get_count_surroundings(x, y))
            surroundings.append(row)
        return surroundings

    @staticmethod
    def get_close_to_other_lines_move(gb: GameBoard, player: int, player_ai: str = "") -> Optional[Move]:
        """Returns Move or None. Some Foo with using 'better' moves close to other lines..."""
        # TODO tests schreiben
        surroundings = NormalAI.get_field_with_count_of_surroundings(gb)
        valid_moves = []
        better_moves = []
        for x in range(0, gb.size_x):
            for y in range(0, gb.size_y):
                if x + 1 < gb.size_x and gb.boxes[x][y].line_right == 0:
                    if surroundings[x][y] < 2 and surroundings[x + 1][y] < 2:
                        valid_moves.append(Move(x, y, 0, player, player_ai))
                        if (gb.boxes[x][y].line_below or y == 0 or gb.boxes[x][y - 1].line_right
                                or y + 1 == gb.size_y or gb.boxes[x][y + 1].line_right):
                            better_moves.append(Move(x, y, 0, player, player_ai))
                if y + 1 < gb.size_y and gb.boxes[x][y].line_below == 0:
                    if surroundings[x][y] < 2 and surroundings[x][y + 1] < 2:
                        valid_moves.append(Move(x, y, 1, player, player_ai))
                        if (gb.boxes[x][y].line_right or x == 0 or gb.boxes[x - 1][y].line_below
                                or x + 1 == gb.size_x or gb.boxes[x + 1][y].line_below):
                            better_moves.append(Move(x, y, 1, player, player_ai))
        if len(better_moves) > 0:
            logging.info(
                "%s: preventing closeable field for opponent, using 'better' move, (%d better, %d possible moves left)"
                % (player_ai, len(better_moves), len(valid_moves))
            )
            return random.choice(better_moves)
        if len(valid_moves) > 0:
            logging.info("%s: preventing closeable field for opponent, (%d possible moves left)" % (
                player_ai, len(valid_moves)))
            return random.choice(valid_moves)
        return None
