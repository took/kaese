import logging
import random
from typing import Optional, List, Union
import copy
from kaese.ai.ai import AI
from kaese.ai.ai_exception import AIException
from kaese.ai.cluster_ai import ClusterAI
from kaese.gameboard.move import Move
from kaese.gameboard.gameboard import GameBoard


class TreeAI(AI):
    """
    TreeAI class represents an AI player that implements an Alpha Beta Search.

    It inherits from the AI class.
    """

    killed: bool = False
    max_moves: int

    cnt_valid_moves: Optional[int]
    cnt_move_nr: Optional[int]
    very_large_numer: int = 1000000000

    gb: GameBoard
    original_player: int
    cnt_deepcopys: int = 0


    def __init__(self, verbose: Union[bool, int] = False, max_moves: int = 42):
        super().__init__(verbose)
        self.max_moves = max_moves
        self.killed = False
        self.cnt_valid_moves = None
        self.cnt_move_nr = None
        self.very_large_numer = 1000000000

    def get_next_move(self, gb: GameBoard, player: int) -> Move:
        """
        Calculates and returns the next move for the AI player.

        Args:
            gb (GameBoard): The game board object.
            player (int): The AI player's identifier.

        Returns:
            Optional[Move]: The next valid move found on the game board, or None if no moves are available.
        """

        self.cnt_deepcopys = 1
        self.gb = copy.deepcopy(gb)
        self.original_player = self.gb.current_player

        if self.original_player != player:
            raise AIException("TreeAI: Wrong Player, can not handle this ...")

        m = self.get_capture_field_move()
        if m:
            return m

        # all_moves = (self.gb.size_x * self.gb.size_y * 2) - self.gb.size_x - self.gb.size_y
        # max_moves = (all_moves // 2) + (all_moves // 5)
        max_moves = self.max_moves
        # print(max_moves)
        if self.gb.remaining_moves > max_moves:
            self.tree_ai_debug("get_next_move: Too many valid_moves (%d>%d), using ClusterAi!"
                               % (self.gb.remaining_moves, max_moves))
            ki = ClusterAI()
            m = ki.get_next_move(self.gb, player)
            m.player_ai = self.gb.player_ai[player]
            return m

        return self.find_best_move()

    def tree_ai_debug(
            self,
            msg: str,
            level: int = 0,
            depth: Optional[int] = None,
            evaluation: Optional[int] = None,
            alpha: Optional[int] = None,
            beta: Optional[int] = None,
            valid_moves: Optional[int] = None,
            move: Optional[Move] = None,
            best_move: Optional[Move] = None
    ) -> None:
        msg = ("tree_ai_debug --- %s --- [dc %d, remaining_moves %d, curPlayer %d, origPlayer %d"
               % (msg, self.cnt_deepcopys, self.gb.remaining_moves, self.gb.current_player, self.original_player))
        if not depth is None:
            spacer = "  " * depth
            msg = "%s%s, depth %d" % (spacer, msg, depth)
        if not evaluation is None:
            msg = "%s, eva %d" % (msg, evaluation)
        if not alpha is None:
            msg = "%s, alpha %d" % (msg, alpha)
        if not beta is None:
            msg = "%s, beta %d" % (msg, beta)
        if not valid_moves is None:
            msg = "%s, valid_moves %d" % (msg, valid_moves)
        if not move is None:
            line_str = "right"
            if move.horizontal:
                line_str = "below"
            msg = ("%s, Move %dx%d line %s, Player: %d (%s)"
                   % (msg, move.x, move.y, line_str, move.player, move.player_ai))
        if not best_move is None:
            line_str = "right"
            if best_move.horizontal:
                line_str = "below"
            msg = ("%s, Move %dx%d line %s, Player: %d (%s)"
                   % (msg, best_move.x, best_move.y, line_str, best_move.player, best_move.player_ai))
        msg = "%s]" % msg
        self.debug(msg, level)

    def get_valid_moves_tree_ai(self) -> List[Move]:
        """
        Return list of valid moves.

        :return: List of Move objects
        """

        player = self.gb.current_player
        player_ai = self.gb.player_ai[player]
        valid_moves = []
        for x, column in enumerate(self.gb.boxes):
            for y, box in enumerate(column):
                if box.line_right == 0 and x + 1 < self.gb.size_x:
                    valid_moves.append(Move(x, y, 0, player, player_ai))
                if box.line_below == 0 and y + 1 < self.gb.size_y:
                    valid_moves.append(Move(x, y, 1, player, player_ai))
        if self.verbose:
            count = len(valid_moves)
            self.tree_ai_debug("get_valid_moves_tree_ai: Found %d valid moves" % count, 3, valid_moves=count)
            for m in valid_moves:
                self.tree_ai_debug("    - move", 3, move=m)
        return valid_moves

    def check_outlines_tree_ai(self, x: int, y: int) -> Optional[Move]:
        """
        Count number of lines that already surround the field on position x, y on the gameboard. If exactly 3 lines
        surround the given box, return the Move object, that represents the move, that is needed to capture this box.
        Else, return None.

        :param x:
        :param y:
        :return:
        """

        # We are not interested in already owned fields
        current_box = self.gb.boxes[x][y]
        if current_box.owner > 0:
            return None

        player = self.gb.current_player
        player_ai = self.gb.player_ai[player]

        right = 0
        below = 0
        left = 0
        above = 0

        # count how many lines are checked around this field
        count_surroundings = 0

        # Check line or border on the right of our box
        if x + 1 < self.gb.size_x:
            if current_box.line_right > 0:
                count_surroundings += 1
                right = 1
        else:
            # Right border of the gameboard
            count_surroundings += 1
            right = 1

        # Check line or border below our box
        if y + 1 < self.gb.size_y:
            if current_box.line_below > 0:
                count_surroundings += 1
                below = 1
        else:
            # Border below our gameboard
            count_surroundings += 1
            below = 1

        # Check line or border to the left of our box (The right line of the box left of our current box)
        if x > 0:
            if self.gb.boxes[x - 1][y].line_right > 0:
                count_surroundings += 1
                left = 1
        else:
            # Left border of gameboard
            count_surroundings += 1
            left = 1

        # Check line or border above our box (The line below the box above our current box)
        if y > 0:
            if self.gb.boxes[x][y - 1].line_below > 0:
                count_surroundings += 1
                above = 1
        else:
            # Upper border of gameboard
            count_surroundings += 1
            above = 1

        # If exactly 3 lines surround the box right now, return the Move object that represents the move,
        # that is needed to capture this box.
        if count_surroundings == 3:
            if right == 0:
                return Move(x, y, 0, player, player_ai)
            if below == 0:
                return Move(x, y, 1, player, player_ai)
            if left == 0:
                return Move(x - 1, y, 0, player, player_ai)
            if above == 0:
                return Move(x, y - 1, 1, player, player_ai)

        # Else, return None
        return None

    def take_back_moves(self, count: int = 1) -> None:
        """
        Take back 'count' moves and truncates the history.

        :param count: How may moves should be taken bake
        :return:
        """

        if self.verbose is int and self.verbose > 2:
            msg = "Take back %d moves." % count
            logging.debug(msg)
            print(msg)

        for _ in range(count):
            self.gb.take_back_one_move()
        self.gb.truncate_history()

    def get_capture_field_move(self) -> Optional[Move]:
        """ Search for fields that can be captured right now and if found return the first one found. """
        size_x = self.gb.size_x
        size_y = self.gb.size_y
        for x in range(0, size_x):
            for y in range(0, size_y):
                m = self.check_outlines_tree_ai(x, y)
                if m:
                    self.tree_ai_debug("get_capture_field_move: capture field", 3, move=m)
                    return m
        self.tree_ai_debug("get_capture_field_move: No (more) capture fields found", 3, move=m)
        return None

    def position_evaluation(self, gb: GameBoard) -> int:
        """
        Evaluate the current game position from the perspective of the original player.

        Args:
            gb (GameBoard): The game board to evaluate.

        Returns:
            int: The evaluated score of the current game position.
        """
        player = self.original_player
        other_player = self.get_other_player(player)
        player_win_counter = gb.win_counter[player]
        other_player_win_counter = gb.win_counter[other_player]
        evaluation = player_win_counter - other_player_win_counter

        # evaluation += gb.moves_made

        # Check if game has ended
        if gb.winner > 0:
            if gb.winner == other_player:
                return evaluation - 100000
            else:
                return evaluation + 100000

        # Check if we already have more than half of the available points!
        all_moves = (gb.size_x * gb.size_y * 2) - gb.size_x - gb.size_y
        if player_win_counter > all_moves // 2:
            return evaluation + 50000
        if other_player_win_counter > all_moves // 2:
            return evaluation - 50000

        return evaluation

    @staticmethod
    def get_other_player(player: int) -> int:
        if player == 1:
            return 2
        else:
            return 1

    def make_ai_move(self, move: Move) -> int:
        """ A "AI move" can consist of multiple "move" objects on the game board. A "AI move" ends when no further
        squares can be closed.

        TODO A problem with our current approach might be, that there could be edge cases where we should "capture"
          most of the available fields but not all of them. We might end up in a situation, where we lose the game (or
          at least lose some points) where we alternatively could have not been to greedy with taking fields that give
          a point immediately.

          Though with the logic of the AlphaBeta Search Tree, where two players play against each other and each one
          takes *one* turn and then the other player is up next, we need to end the "AI move" in a way, that after
          this (set of) move(s), the other player is up next!

          So we cannot just skip the last three or four fields that could have been captured and end with an gameboard
          where the current player still has to decide, which move to make next.

          Maybe we could even use some parts of the logic from the ClusterAI to reduce the amount of "valid" moves that
          are tested by the AlphaBeta Search Tree.
        """
        self.gb.make_move(move, print_it=False)
        cnt_moves = 1
        if self.gb.current_player == move.player and self.gb.winner == 0:
            # It's still our turn!
            m = self.get_capture_field_move()
            while m and self.gb.winner == 0:
                self.gb.make_move(m, print_it=False)
                cnt_moves += 1
                if self.gb.winner == 0:
                    m = self.get_capture_field_move()
        return cnt_moves

    def alpha_beta_search(self, depth: int, alpha: int, beta: int) -> int:
        """
        Perform Alpha-Beta pruning search with evaluation and depth limits.

        Args:
            depth (int): The current depth of the search tree.
            alpha (int): The lower bound for the best achievable score.
            beta (int): The upper bound for the best achievable score.

        Returns:
            int: The evaluated score of the current game state.
        """

        if self.killed:
            # Die if requested
            return self.very_large_numer

        evaluation = self.position_evaluation(self.gb)
        if abs(evaluation) > 9000:
            self.tree_ai_debug(
                "alpha_beta_search: Return Evaluation over nine thousand!",
                1,
                depth,
                evaluation
            )
            return evaluation
        if depth == 0:
            self.tree_ai_debug(
                "alpha_beta_search: Return Evaluation because depth is 0.",
                2,
                depth,
                evaluation
            )
            return evaluation

        valid_moves = self.get_valid_moves_tree_ai()
        cnt_valid_moves = len(valid_moves)
        if cnt_valid_moves == 0:
            msg = ("alpha_beta_search: This is unexpected. Return Evaluation %d when len(valid_moves) == 0. "
                   "This should not happen. If the game has ended, the value should be over 9000!") % evaluation
            logging.warning(msg)
            self.tree_ai_debug(msg, 0, depth, evaluation)
            return evaluation

        if self.verbose:
            msg = ("alpha_beta_search: Recursively call alpha_beta_search for each valid move, "
                   "next up: Player %d (I am %d)") % (self.gb.current_player, self.original_player)
            self.tree_ai_debug(msg, 2, depth, evaluation, alpha, beta, cnt_valid_moves)
        if self.gb.current_player == 1:
            value = -self.very_large_numer
            for m in valid_moves:
                if self.verbose:
                    self.tree_ai_debug(
                        "alpha_beta_search:     Recursively evaluating Move  -",
                        3,
                        depth,
                        evaluation,
                        move=m
                    )
                self.cnt_deepcopys += 1
                cnt_moves = self.make_ai_move(m)
                value = max(value, self.alpha_beta_search(depth - 1, alpha, beta))
                self.take_back_moves(cnt_moves)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = self.very_large_numer
            for m in valid_moves:
                if self.verbose:
                    self.tree_ai_debug(
                        "alpha_beta_search:     Recursively evaluating Move  -",
                        3,
                        depth,
                        evaluation,
                        move=m
                    )
                self.cnt_deepcopys += 1
                cnt_moves = self.make_ai_move(m)
                value = min(value, self.alpha_beta_search(depth - 1, alpha, beta))
                self.take_back_moves(cnt_moves)
                beta = min(beta, value)
                if alpha >= beta:
                    break

        return value

    def find_best_move(self) -> Move:
        """
        Find the best move using Alpha-Beta pruning.

        Returns:
            Move: The best move to make.

        Raises:
            AIException: If no valid moves are found.
        """

        best_value: int = -self.very_large_numer
        best_move: Optional[Move] = None
        valid_moves: List[Move] = self.get_valid_moves_tree_ai()
        random.shuffle(valid_moves)

        self.cnt_valid_moves: int = len(valid_moves)
        self.cnt_move_nr: int = 0
        cnt_eva_null_moves_found: int = 0

        max_depth: int = 4
        if True and self.cnt_valid_moves < 30:
            max_depth += 1
        if True and self.cnt_valid_moves < 15:
            max_depth += 1

        for move in valid_moves:
            if (True  # Set to True if you want to enable the feature "Skip if eva0 found too often".
                    and max_depth > 5 and best_value == 0 and self.cnt_valid_moves > 10
                    and cnt_eva_null_moves_found > self.cnt_valid_moves // 10):
                self.tree_ai_debug(
                    "find_best_move: Found Eva==0 too often. Break.",
                    0,
                    max_depth,
                    best_value,
                    -self.very_large_numer,
                    self.very_large_numer,
                    self.cnt_valid_moves,
                    move
                )
                break
            self.cnt_move_nr += 1
            self.cnt_deepcopys += 1
            cnt_moves = self.make_ai_move(move)
            self.tree_ai_debug(
                "find_best_move: Test Move %d of %d, made %d moves in one step. Next Up: Player %d (I am %d)!"
                % (self.cnt_move_nr, self.cnt_valid_moves, cnt_moves, self.gb.current_player, self.original_player),
                0,
                max_depth,
                best_value,
                -self.very_large_numer,
                self.very_large_numer,
                self.cnt_valid_moves,
                move,
                best_move
            )
            value = self.alpha_beta_search(max_depth - 1, -self.very_large_numer, self.very_large_numer)
            self.take_back_moves(cnt_moves)
            self.tree_ai_debug(
                "find_best_move:   Tested Move %d with Eva %d (Best was %d). #Eva0: %d"
                % (self.cnt_move_nr, value, best_value, cnt_eva_null_moves_found),
                0,  # TODO Set to 1
                max_depth,
                value,
                valid_moves=self.cnt_valid_moves,
                move=move,
                best_move=best_move
            )

            if value == 0:
                cnt_eva_null_moves_found += 1

            if value > best_value:
                best_value = value
                best_move = move

            if True and max_depth > 3 and best_value > 0:
                self.tree_ai_debug(
                    "find_best_move: Found Eva>0. Break.",
                    0,
                    max_depth,
                    best_value,
                    -self.very_large_numer,
                    self.very_large_numer,
                    self.cnt_valid_moves,
                    move
                )
                break

        if not best_move:
            raise AIException("No more valid moves found, game seems to be ended already.")

        return best_move
