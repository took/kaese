from kaese.gameboard.gameboard_exception import GameboardException


class InvalidMoveException(GameboardException):
    """If Gameboard.is_valid_move() explicit raise an exception, it shall be of this type."""
    pass
