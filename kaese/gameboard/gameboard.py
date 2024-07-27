from typing import Dict, List, Optional, Union
import logging
from kaese.gameboard.invalid_move_exception import InvalidMoveException
from kaese.gameboard.box import Box
from kaese.gameboard.move import Move


class GameBoard:
    """
    Container for the current game state and methods that implement the game rules.

    Attributes:
        size_x (int): Size of the gameboard in "boxes" (not pixels).
        size_y (int): Size of the gameboard in "boxes" (not pixels).
        verbose (Union[bool, int]): Level of verbosity for game messages (bool or int in range 0-3).
        boxes (List[List[Box]]): 2D matrix of all boxes on the board.
        current_player (int): The current player (1 or 2).
        player_ai (Dict[int, str]): Dictionary mapping player number to player type ("Human" or "AI").
        winner (int): 0 for no winner yet, 1/2 for player 1/2 won, 3 for draw.
        win_counter (Dict[int, int]): Dictionary storing how many boxes each player owns.
        moves_made (int): Number of moves that have been made.
        remaining_moves (int): Number of remaining (valid) moves.
        last_move (Optional[Move]): Last move made, used to highlight the line in the GUI.
        move_history (List[Move]): List of moves made in the game.
        move_history_pointer (int): Pointer to the current position in the move history.
    """
    size_x: int  # size of the gameboard in "boxes" (not pixels)
    size_y: int
    verbose: Union[bool, int]
    boxes: List[List[Box]]  # 2D matrix of all boxes on the board
    current_player: int  # 1 or 2
    player_ai: Dict[int, str]
    winner: int  # 0: no winner yet, 1/2: player 1/2 won, 3: draw
    win_counter: Dict[int, int]  # how many boxes did the players already own
    moves_made: int  # how many moves were already made
    remaining_moves: int  # how many (valid) moves left
    last_move: Optional[Move]  # last move, stored to highlight that line in some way in the GUI
    move_history: List[Move]
    move_history_pointer: int

    def __init__(self, size_x: int = 12, size_y: int = 12, verbose: Union[bool, int] = False) -> None:
        """
        Initialize a GameBoard object with the specified size and verbosity level.

        :param size_x: Size of the gameboard in the x-direction (default is 12).
        :type size_x: int
        :param size_y: Size of the gameboard in the y-direction (default is 12).
        :type size_y: int
        :param verbose: Level of verbosity for game messages (bool or int in range 0-3, default is False).
        :type verbose: Union[bool, int]
        """
        self.size_x = size_x
        self.size_y = size_y
        self.verbose = verbose
        self.boxes = []
        self.win_counter = {1: 0, 2: 0}
        self.last_move = None
        for x in range(self.size_x):
            column = []
            for y in range(self.size_y):
                column.append(Box())
            self.boxes.append(column)
        self.moves_made = 0
        self.remaining_moves = (self.size_x * self.size_y * 2) - self.size_x - self.size_y

        self.current_player = 1  # 1 or 2
        self.player_ai = {
            1: "Human",
            2: "Human"
        }
        self.winner = 0  # 0: no winner yet, 1/2: player 1/2 won, 3: draw
        self.win_counter = {1: 0, 2: 0}  # how many boxes did the players already own
        self.last_move = None  # last move, stored to highlight that line in some way in the GUI
        self.move_history = []
        # move_history_pointer
        #  0: Pointing to no move.
        #  1 - len(self.move_history): Point to self.move_history[self.move_history_pointer-1].
        self.move_history_pointer = 0

        logging.info("Gameboard initialized")

    def check_and_set_new_owner(self, x: int, y: int, new_owner: int, print_it: bool = True) -> int:
        """
        Check if a certain box now has a new owner and return 0 by default, else 1 if the new box is owned.

        :param x: The x-coordinate of the box.
        :type x: int
        :param y: The y-coordinate of the box.
        :type y: int
        :param new_owner: The new owner of the box.
        :type new_owner: int
        :param print_it: If True, print the status (default is True).
        :type print_it: bool
        :return: 0 if the box is not owned by the new owner, 1 if the box is owned by the new owner.
        :rtype: int
        """
        if x >= self.size_x or y >= self.size_y:
            return 0
        if self.boxes[x][y].owner > 0:
            return 0
        border_count = self.get_count_surroundings(x, y)
        if border_count == 4:
            self.boxes[x][y].owner = new_owner
            if print_it:
                logging.info("New Owner for x: %d, y: %d is player %d" % (x, y, new_owner))
            # TODO Maybe refactor this: Do not increment but count all fields instead
            self.win_counter[new_owner] += 1
            return 1
        return 0

    def get_count_surroundings(self, x: int, y: int) -> int:
        """
        Get the count of surrounding elements around the specified coordinates.

        :param x: The x-coordinate of the element 0 - size_x-1.
        :type x: int
        :param y: The y-coordinate of the element 0 - size_y-1.
        :type y: int
        :return: The count of surrounding elements 0 - 4.
        :rtype: int
        """
        border_count = 0
        if x + 1 < self.size_x:
            if self.boxes[x][y].line_right > 0:
                border_count += 1
        else:
            border_count += 1
        if y + 1 < self.size_y:
            if self.boxes[x][y].line_below > 0:
                border_count += 1
        else:
            border_count += 1
        if x > 0:
            if self.boxes[x - 1][y].line_right > 0:
                border_count += 1
        else:
            border_count += 1
        if y > 0:
            if self.boxes[x][y - 1].line_below > 0:
                border_count += 1
        else:
            border_count += 1
        return border_count

    def make_move(
            self,
            move: Move,
            print_it: bool = True,
            skip_append_to_history: bool = False,
            ignore_current_selected_player: bool = False
    ) -> None:
        """
        Make a move.

        :param move: The move to be made.
        :type move: Move
        :param print_it: If True, print the move (default is True).
        :type print_it: bool
        :param skip_append_to_history: If True, skip appending the move to the history (default is False).
        :type skip_append_to_history: bool
        :param ignore_current_selected_player: If True, ignore the current selected player (default is False).
        :type ignore_current_selected_player: bool
        :return: None
        """
        if print_it:
            msg = "Move made by Player %d (%s): x %d, y %d, horizontal %d" % \
                  (move.player, move.player_ai, move.x, move.y, move.horizontal)
            logging.info(msg)
            print(msg)
        self.is_valid_move(move, ignore_current_selected_player)
        box = self.boxes[move.x][move.y]
        if move.horizontal == 1:
            box.line_below = move.player
        else:
            box.line_right = move.player
        captured_boxes = 0
        captured_boxes += self.check_and_set_new_owner(move.x, move.y, move.player, print_it)
        captured_boxes += self.check_and_set_new_owner(move.x + 1, move.y, move.player, print_it)
        captured_boxes += self.check_and_set_new_owner(move.x, move.y + 1, move.player, print_it)
        if captured_boxes == 0:
            if print_it and self.verbose:
                msg = "No new Owner, next Player's turn"
                logging.debug(msg)
                print(msg)
            self.current_player = 1 if self.current_player != 1 else 2
        self.last_move = move
        if not skip_append_to_history:
            self.move_history.append(move)
            self.move_history_pointer += 1
        self.moves_made += 1
        self.remaining_moves -= 1
        if self.remaining_moves == 0:
            if self.win_counter[1] > self.win_counter[2]:
                self.winner = 1
            elif self.win_counter[2] > self.win_counter[1]:
                self.winner = 2
            else:
                self.winner = 3

    def take_back_one_move(self) -> None:
        """
        Take back the last move made in the game.

        This method reverts the game state to the state before the last move was made.
        It updates the boxes matrix, current player, moves_made, remaining_moves, last_move,
        move_history_pointer, win_counter and winner.

        :return: None
        """
        self.move_history_pointer -= 1
        move = self.move_history[self.move_history_pointer]
        if self.boxes[move.x][move.y].owner > 0:
            # TODO Maybe refactor this: Do not increment but count all fields instead
            self.win_counter[self.boxes[move.x][move.y].owner] -= 1
            self.boxes[move.x][move.y].owner = 0
        if move.horizontal == 0:
            # Vertical line, check boxes left and right of line (x and x+1)
            self.boxes[move.x][move.y].line_right = 0
            if move.x + 1 < self.size_x:
                if self.boxes[move.x + 1][move.y].owner > 0:
                    # TODO Maybe refactor this: Do not increment but count all fields instead
                    self.win_counter[self.boxes[move.x + 1][move.y].owner] -= 1
                    self.boxes[move.x + 1][move.y].owner = 0
        else:
            # Horizontal line, check boxes above and below line (y and y+1)
            self.boxes[move.x][move.y].line_below = 0
            if move.y + 1 < self.size_y:
                if self.boxes[move.x][move.y + 1].owner > 0:
                    # TODO Maybe refactor this: Do not increment but count all fields instead
                    self.win_counter[self.boxes[move.x][move.y + 1].owner] -= 1
                    self.boxes[move.x][move.y + 1].owner = 0
        if self.move_history_pointer > 0:
            self.current_player = move.player
        else:
            self.current_player = 1
        self.moves_made -= 1
        self.remaining_moves += 1
        if self.winner > 0:
            self.winner = 0
        # Update last_move
        if 0 < self.move_history_pointer <= len(self.move_history):
            self.last_move = self.move_history[self.move_history_pointer - 1]
        else:
            self.last_move = None

    def truncate_history(self) -> None:
        # Truncate history after current move
        self.move_history = self.move_history[:self.move_history_pointer]

    def is_valid_move(self, move: Move, ignore_current_selected_player: bool = False) -> bool:
        """
        Check if a move is valid, otherwise raise an InvalidMoveException.

        :param move: The move to be checked for validity.
        :type move: Move
        :param ignore_current_selected_player: If True, ignore the current selected player (default is False).
        :type ignore_current_selected_player: bool
        :return: True if the move is valid, otherwise an InvalidMoveException will be raised.
        :rtype: bool
        """
        if not ignore_current_selected_player:
            if move.player != self.current_player:
                raise InvalidMoveException("Invalid move: Wrong player", move.player, self.current_player)
            if move.player_ai != self.player_ai[self.current_player]:
                raise InvalidMoveException(
                    "Invalid move: Wrong player_ai %s, should be %s for Player %d" %
                    (move.player_ai, self.player_ai[self.current_player], self.current_player)
                )
        if move.x < 0 or move.x >= self.size_x or move.y < 0 or move.y >= self.size_y:
            raise InvalidMoveException("Invalid move: Bad coordinates", move.x, move.y, self.size_x, self.size_y)
        box = self.boxes[move.x][move.y]
        if move.horizontal == 1:
            if move.y + 1 >= self.size_y:
                raise InvalidMoveException(
                    "Invalid move: Bad coordinates for horizontal line",
                    move.x,
                    move.y,
                    self.size_x,
                    self.size_y
                )
            if box.line_below > 0:
                raise InvalidMoveException("Invalid move: Line below already occupied", move.x, move.y)
        else:
            if move.x + 1 >= self.size_x:
                raise InvalidMoveException(
                    "Invalid move: Bad coordinates for vertical line",
                    move.x,
                    move.y,
                    self.size_x,
                    self.size_y
                )
            if box.line_right > 0:
                raise InvalidMoveException("Invalid move: Line right already occupied", move.x, move.y)
        return True
