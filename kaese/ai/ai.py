import logging
from abc import ABC, abstractmethod
from typing import Union

from kaese.gameboard.gameboard import GameBoard
from kaese.gameboard.move import Move


class AI(ABC):
    """Abstract AI class"""

    verbose: Union[bool, int]

    def __init__(self, verbose: Union[bool, int] = False) -> None:
        self.verbose = verbose

    def debug(self, msg: str, level: int = 0) -> None:
        """
        Print debug message.

        Args:
            msg (string): The message to print
            level (int): Debug level

        Returns:
            Void
        """
        msg = "    %s Verbose %d: %s" % (self.__class__.__name__, level, msg)
        if ((isinstance(self.verbose, bool) and self.verbose)
                or (isinstance(self.verbose, int) and self.verbose > 0 and self.verbose >= level)):
            logging.debug(msg)
            print(msg)
        elif level == 0:
            logging.debug(msg)

    @abstractmethod
    def get_next_move(self, game_board: GameBoard, player: int) -> Move:
        """Calculate next move."""
        pass
