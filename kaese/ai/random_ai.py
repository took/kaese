from typing import List
import random
from kaese.ai.ai import AI
from kaese.ai.ai_exception import AIException
from kaese.gameboard.move import Move
from kaese.gameboard.gameboard import GameBoard


class RandomAI(AI):
    """
    RandomAI class represents an AI player that selects a random valid move on the game board.

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

        Raises:
            Exception: If no more valid moves are found on the game board.
        """
        player_ai = self.__class__.__name__

        if gb.current_player != player:
            raise AIException("RandomAI: Wrong Player, can not handle this...")

        return RandomAI.get_random_valid_move(gb, player, player_ai)

    @staticmethod
    def get_random_valid_move(gb: GameBoard, player: int, player_ai: str = "") -> Move:
        """
        Returns a random valid move from the available moves on the game board.

        Args:
            gb (GameBoard): The game board object.
            player (int): The AI player's identifier.
            player_ai (string): Class name of used AI

        Returns:
            Move: The randomly selected valid move.

        Raises:
            Exception: If no more valid moves are found on the game board.
        """
        gb_size_x = gb.size_x
        gb_size_y = gb.size_y
        valid_moves: List[Move] = []

        for x, row in enumerate(gb.boxes):
            for y, box in enumerate(row):
                if box.line_right == 0 and x + 1 < gb_size_x:
                    valid_moves.append(Move(x, y, 0, player, player_ai))
                if box.line_below == 0 and y + 1 < gb_size_y:
                    valid_moves.append(Move(x, y, 1, player, player_ai))

        if not valid_moves:
            raise AIException("No more valid moves found. The game seems to be already ended.")

        return random.choice(valid_moves)
