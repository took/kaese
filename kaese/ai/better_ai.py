from typing import Dict, List, Optional
import random
import logging
from kaese.ai.ai import AI
from kaese.ai.ai_exception import AIException
from kaese.ai.normal_ai import NormalAI
from kaese.ai.random_ai import RandomAI
from kaese.ai.simple_ai import SimpleAI
from kaese.gameboard.move import Move
from kaese.gameboard.gameboard import GameBoard


class BetterAI(AI):
    """
    BetterAI class represents an AI player that has improved behaviour.

    It acts just like the NormalAI but if it has to fall back on a random move, it instead searches for a move,
    that will allow the opponent to take just one field. Else, it selects a random valid move.

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
            raise AIException("BetterAI: Wrong Player, can not handle this...")

        # Check if any fields can be captured immediately and return the first found move
        capture_field_move = SimpleAI.get_capture_field_move(gb, player, player_ai)
        if capture_field_move:
            return capture_field_move

        surroundings_count_matrix = NormalAI.get_field_with_count_of_surroundings(gb)

        # TODO versuche möglichst viele einser-cluster zu bauen

        # before using "any valid move" search for moves where surroundings<2
        move = BetterAI.get_better_moves(gb, player, surroundings_count_matrix, player_ai)
        if move:
            return move

        # try to give the opponent only 1 field!
        # TODO in eigene methode auslagern und tests für schreiben
        valid_moves = []
        for x in range(0, gb.size_x):
            for y in range(0, gb.size_y):
                if surroundings_count_matrix[x][y] == 2:
                    # logging.debug("phase 3: found", x, y)
                    kanten_der_umrandung = BetterAI.get_surroundings(gb, x, y)
                    # if links und oben besetzt
                    if kanten_der_umrandung["links"] and kanten_der_umrandung["oben"]:
                        if (x + 1 == gb.size_x or surroundings_count_matrix[x + 1][y] < 2) and (
                                y + 1 == gb.size_y or surroundings_count_matrix[x][y + 1] < 2):
                            if x < gb.size_x:
                                # rechts
                                valid_moves.append(Move(x, y, 0, player, player_ai))
                            if y < gb.size_y:
                                # unten
                                valid_moves.append(Move(x, y, 1, player, player_ai))
                    # if rechts und oben besetzt
                    if kanten_der_umrandung["rechts"] and kanten_der_umrandung["oben"]:
                        if ((x == 0 or surroundings_count_matrix[x - 1][y] < 2)
                                and (y + 1 == gb.size_y or surroundings_count_matrix[x][y + 1] < 2)):
                            if x > 0:
                                # links
                                valid_moves.append(Move(x - 1, y, 0, player, player_ai))
                                # logging.debug(x - 1, y, 0, "rechts oben: links")
                            if y < gb.size_y:
                                # unten
                                valid_moves.append(Move(x, y, 1, player, player_ai))
                                # logging.debug(x, y, 1, "rechts oben: unten")
                    # if links und unten besetzt
                    if kanten_der_umrandung["links"] and kanten_der_umrandung["unten"]:
                        if ((x + 1 == gb.size_x or surroundings_count_matrix[x + 1][y] < 2)
                                and (y == 0 or surroundings_count_matrix[x][y - 1] < 2)):
                            if x < gb.size_x:
                                # rechts
                                valid_moves.append(Move(x, y, 0, player, player_ai))
                                # logging.debug(x, y, 0, "links unten: rechts")
                            if y > 0:
                                # oben
                                valid_moves.append(Move(x, y - 1, 1, player, player_ai))
                                # logging.debug(x, y - 1, 1, "links unten: oben")
                    # if rechts und unten besetzt
                    if kanten_der_umrandung["rechts"] and kanten_der_umrandung["unten"]:
                        if ((x == 0 or surroundings_count_matrix[x - 1][y] < 2)
                                and (y == 0 or surroundings_count_matrix[x][y - 1] < 2)):
                            if x > 0:
                                # links
                                valid_moves.append(Move(x - 1, y, 0, player, player_ai))
                                # logging.debug(x - 1, y, 0, "rechts unten: links")
                            if y > 0:
                                # oben
                                valid_moves.append(Move(x, y - 1, 1, player, player_ai))
                                # logging.debug(x, y - 1, 1, "rechts unten: oben")
                    # if links und rechts besetzt
                    if kanten_der_umrandung["links"] and kanten_der_umrandung["rechts"]:
                        if ((y == 0 or surroundings_count_matrix[x][y - 1] < 2)
                                and (y + 1 == gb.size_y or surroundings_count_matrix[x][y + 1] < 2)):
                            if y > 0:
                                # oben
                                valid_moves.append(Move(x, y - 1, 1, player, player_ai))
                                # logging.debug(x, y - 1, 1, "links rechts: oben")
                            if y < gb.size_y:
                                # unten
                                valid_moves.append(Move(x, y, 1, player, player_ai))
                                # logging.debug(x, y, 1, "links rechts: unten")
                    # if oben und unten besetzt
                    if kanten_der_umrandung["oben"] and kanten_der_umrandung["unten"]:
                        if ((x == 0 or surroundings_count_matrix[x - 1][y] < 2)
                                and (x + 1 == gb.size_x or surroundings_count_matrix[x + 1][y] < 2)):
                            if x < gb.size_x:
                                # rechts
                                valid_moves.append(Move(x, y, 0, player, player_ai))
                                # logging.debug(x, y, 0, "oben unten: rechts")
                            if x > 0:
                                # links
                                valid_moves.append(Move(x - 1, y, 0, player, player_ai))
                                # logging.debug(x - 1, y, 1, "oben unten: links")
        if len(valid_moves) > 0:
            logging.info("%s: giving opponent only 1 field, (%d possible moves left)" % (
                player_ai, len(valid_moves)))
            return random.choice(valid_moves)

        # Fallback: Use a random valid move
        logging.info("%s: Using fallback (a random valid move)" % player_ai)
        return RandomAI.get_random_valid_move(gb, player, player_ai)

    @staticmethod
    def get_surroundings(gb: GameBoard, x: int, y: int) -> Dict[str, int]:
        rechts = 0
        unten = 0
        links = 0
        oben = 0

        if x + 1 < gb.size_x:
            if gb.boxes[x][y].line_right > 0:
                rechts = 1
        else:
            # rechter spielfeld rand
            rechts = 1

        if y + 1 < gb.size_y:
            if gb.boxes[x][y].line_below > 0:
                unten = 1
        else:
            # unterer spielfeld rand
            unten = 1

        if x > 0:
            if gb.boxes[x - 1][y].line_right > 0:
                links = 1
        else:
            # linker spielfeld rand
            links = 1

        if y > 0:
            if gb.boxes[x][y - 1].line_below > 0:
                oben = 1
        else:
            # oberer spielfeld rand
            oben = 1

        return {"rechts": rechts, "links": links, "unten": unten, "oben": oben}

    @staticmethod
    def get_better_moves(
            gb: GameBoard,
            player: int,
            surroundings_count_matrix: List[List[int]],
            player_ai: str = ""
    ) -> Optional[Move]:
        """Returns Move or None. Some Foo with using 'better' moves close to other lines..."""
        lists = BetterAI.get_better_moves_lists(gb, player, surroundings_count_matrix, player_ai)
        better_moves = lists["better_moves"]
        good_moves = lists["good_moves"]
        if len(better_moves) > 0:
            logging.info(
                "%s: Preventing closeable field for opponent, using 'better' move, (%d better, %d good moves left)"
                % (
                    player_ai, len(better_moves), len(good_moves)
                )
            )
            return random.choice(better_moves)
        if len(good_moves) > 0:
            logging.info("%s: preventing closeable field for opponent, (%d good moves left)" % (
                player_ai, len(good_moves)))
            return random.choice(good_moves)
        return None

    @staticmethod
    def get_better_moves_lists(
            gb: GameBoard,
            player: int,
            surroundings_count_matrix: List[List[int]],
            player_ai: str = ""
    ) -> Dict[str, List[Move]]:
        """
        Returns Move or False. Generates a list of 'better' moves based on the given game board, player,
        and surroundings.

        Args:
            gb: A GameBoard object representing the game board.
            player: An integer representing the player.
            surroundings_count_matrix: Count of the surroundings of each box on the current game board.
            player_ai: (Optional) A string representing the AI player.

        Returns:
            Dict[str, List[Move]]: A dictionary containing two lists of Move objects - 'better_moves' and 'good_moves'.
        """
        good_moves = []
        better_moves = []
        for x in range(0, gb.size_x):
            for y in range(0, gb.size_y):
                # -- Right line
                # if we are not at the right edge and line_right is still free
                if x + 1 < gb.size_x and gb.boxes[x][y].line_right == 0:
                    # Are both fields usable? Is this a move where I don't gift anything to the opponent?
                    if surroundings_count_matrix[x][y] < 2 and surroundings_count_matrix[x + 1][y] < 2:
                        good_moves.append(Move(x, y, 0, player, player_ai))
                        # right angle with bottom left of the current vertical line
                        if gb.boxes[x][y].line_below:
                            better_moves.append(Move(x, y, 0, player, player_ai))
                        # right angle with bottom right of the current vertical line
                        if x + 1 < gb.size_x:
                            if gb.boxes[x + 1][y].line_below:
                                better_moves.append(Move(x, y, 0, player, player_ai))
                        # right angle with top left of the current vertical line
                        if y > 0:
                            if gb.boxes[x][y - 1].line_below:
                                better_moves.append(Move(x, y, 0, player, player_ai))
                        # right angle with top right of the current vertical line
                        if y > 0 and x + 1 < gb.size_x:
                            if gb.boxes[x + 1][y - 1].line_below:
                                better_moves.append(Move(x, y, 0, player, player_ai))
                # -- Bottom line
                # if we are not at the bottom edge and line_below is still free
                if y + 1 < gb.size_y and gb.boxes[x][y].line_below == 0:
                    # Are both fields usable? Is this a move where I don't gift anything to the opponent?
                    if surroundings_count_matrix[x][y] < 2 and surroundings_count_matrix[x][y + 1] < 2:
                        good_moves.append(Move(x, y, 1, player, player_ai))
                        # right angle with top right of the current horizontal line
                        if gb.boxes[x][y].line_right:
                            better_moves.append(Move(x, y, 1, player, player_ai))
                        # right angle with top left of the current horizontal line
                        if x > 0:
                            if gb.boxes[x - 1][y].line_right:
                                better_moves.append(Move(x, y, 1, player, player_ai))
                        # right angle with bottom right of the current horizontal line
                        if y + 1 < gb.size_y:
                            if gb.boxes[x][y + 1].line_right:
                                better_moves.append(Move(x, y, 1, player, player_ai))
                        # right angle with bottom left of the current horizontal line
                        if x > 0 and y + 1 < gb.size_y:
                            if gb.boxes[x - 1][y + 1].line_right:
                                better_moves.append(Move(x, y, 1, player, player_ai))
        return {"better_moves": better_moves, "good_moves": good_moves}
