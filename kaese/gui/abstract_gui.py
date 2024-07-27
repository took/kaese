from abc import ABC, abstractmethod
from typing import Union

from kaese.gameboard.gameboard import GameBoard
from kaese.gameboard.move import Move


class AbstractGui(ABC):
    """
    Abstract Gui class to be used with Pygame only. This class exists, to avoid circular imports
    when passing the Gui object to the PlayingSurface.

    Also used for TkinterGui as a boilerplate.
    """
    gb: GameBoard
    screen_width: int
    screen_height: int
    verbose: Union[bool, int]

    @abstractmethod
    def make_move(self, move: Move) -> None:
        """
        Make move on gb and redraw gameboard.

        May be called from external AIs to make a move.
        """
        pass

    @abstractmethod
    def update_player_ai(self, player: int, player_ai: str = "Human") -> None:
        """
        Call this method, whenever the player_ai for one of both players changes.

        May be called from main.py when a new game is loaded from a saved game.
        """
        pass

    def kill_tree_ai(self) -> None:
        """ Kill any running AI threads """
        pass

    def main_loop(self) -> None:
        """ Call the main loop of the GUI here! """
        pass
