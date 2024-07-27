from kaese.ai.ai import AI
from kaese.ai.ai_exception import AIException
from kaese.gameboard.move import Move
from kaese.gameboard.gameboard import GameBoard


class StupidAI(AI):
    """
    StupidAI class represents an AI player that selects the first available valid move on the game board.

    It inherits from the AI class.
    """

    def get_next_move(self, gb: GameBoard, player: int) -> Move:
        """
        Returns the next move for the AI player.

        Args:
            gb (GameBoard): The game board object.
            player (int): The AI player's identifier.

        Returns:
            Move: The first valid move found on the game board.

        Raises:
            Exception: If no more valid moves are found on the game board.
        """
        player_ai = self.__class__.__name__

        if gb.current_player != player:
            raise AIException("StupidAI: Wrong Player, can not handle this...")

        return StupidAI.get_first_valid_move(gb, player, player_ai)

    @staticmethod
    def get_first_valid_move(gb: GameBoard, player: int, player_ai: str = "") -> Move:
        """
        Returns the first valid move found on the game board.

        Args:
            gb (GameBoard): The game board object.
            player (int): The AI player's identifier.
            player_ai: (Optional) A string representing the AI player.

        Returns:
            Move: The first valid move found on the game board.

        Raises:
            Exception: If no more valid moves are found on the game board.
        """
        for x, row in enumerate(gb.boxes):
            for y, box in enumerate(row):
                if box.line_right == 0 and x + 1 < gb.size_x:
                    return Move(x, y, 0, player, player_ai)
                if box.line_below == 0 and y + 1 < gb.size_y:
                    return Move(x, y, 1, player, player_ai)

        raise AIException("No more valid moves found; the game seems to be already ended.")
