from typing import Optional
import logging
from kaese.ai.ai import AI
from kaese.ai.ai_exception import AIException
from kaese.ai.random_ai import RandomAI
from kaese.gameboard.move import Move
from kaese.gameboard.gameboard import GameBoard


class SimpleAI(AI):
    """
    SimpleAI class represents an AI player that looks for boxes that can be closed right now. If none found,
    it selects a random valid move.

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
            raise AIException("SimpleAI: Wrong Player, can not handle this...")

        # Check if any fields can be captured immediately and return the first found move
        capture_field_move = SimpleAI.get_capture_field_move(gb, player, player_ai)
        if capture_field_move:
            return capture_field_move

        # Fallback: Use a random valid move
        logging.info("%s: Using fallback (a random valid move)" % player_ai)
        return RandomAI.get_random_valid_move(gb, player, player_ai)

    @staticmethod
    def get_capture_field_move(gb: GameBoard, player: int, player_ai: str = "") -> Optional[Move]:
        """
        Searches for fields that can be captured immediately and returns the first found move.

        Args:
            gb (GameBoard): The game board object.
            player (int): The AI player's identifier.
            player_ai (string): Class name of used AI

        Returns:
            Optional[Move]: The move to capture a field, or None if no fields can be captured.
        """
        for x in range(0, gb.size_x):
            for y in range(0, gb.size_y):
                move = SimpleAI.check_surroundings(gb, player, x, y, player_ai)
                if move:
                    logging.info("%s: Capture field" % player_ai)
                    return move

        return None

    @staticmethod
    def check_surroundings(gb: GameBoard, player: int, x: int, y: int, player_ai: str = "") -> Optional[Move]:
        """
        Checks the surroundings of a field and returns a move if the field can be captured.

        Args:
            gb (GameBoard): The game board object.
            player (int): The AI player's identifier.
            x (int): The x-coordinate of the field.
            y (int): The y-coordinate of the field.
            player_ai (string): Class name of used AI

        Returns:
            Optional[Move]: The move to capture the field, or None if the field cannot be captured.
        """
        if gb.boxes[x][y].owner > 0:
            return None

        right = 0
        bottom = 0
        left = 0
        top = 0
        surrounding_lines = 0

        # Check right side
        if x + 1 < gb.size_x:
            if gb.boxes[x][y].line_right > 0:
                surrounding_lines += 1
                right = 1
        else:
            surrounding_lines += 1
            right = 1

        # Check bottom side
        if y + 1 < gb.size_y:
            if gb.boxes[x][y].line_below > 0:
                surrounding_lines += 1
                bottom = 1
        else:
            surrounding_lines += 1
            bottom = 1

        # Check left side (right side of the box to the left)
        if x > 0:
            if gb.boxes[x - 1][y].line_right > 0:
                surrounding_lines += 1
                left = 1
        else:
            surrounding_lines += 1
            left = 1

        # Check top side (bottom side of the box above)
        if y > 0:
            if gb.boxes[x][y - 1].line_below > 0:
                surrounding_lines += 1
                top = 1
        else:
            surrounding_lines += 1
            top = 1

        if surrounding_lines == 3:
            if right == 0:
                return Move(x, y, 0, player, player_ai)
            if bottom == 0:
                return Move(x, y, 1, player, player_ai)
            if left == 0:
                return Move(x - 1, y, 0, player, player_ai)
            if top == 0:
                return Move(x, y - 1, 1, player, player_ai)

        return None
