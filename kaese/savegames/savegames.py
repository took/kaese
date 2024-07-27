import json
import logging
import os
from typing import Dict, List, Union

from kaese.gameboard.box import Box
from kaese.gameboard.gameboard import GameBoard
from kaese.gameboard.move import Move
from kaese.savegames.save_game_exception import SaveGameException


class Savegames:

    @staticmethod
    def save_game(gameboard: GameBoard, filename: str, overwrite: bool = False) -> None:
        """
        Save gameboard to json file.

        :param gameboard: The GameBoard object to be saved.
        :type gameboard: GameBoard
        :param filename: The filename in the ./savegames/ folder to save to.
        :type filename: str
        :param overwrite: If True, overwrite the file if it already exists. Else, raise an exception if the file exists.
        :type overwrite: bool
        :return: None
        """
        full_path = Savegames.extend_filename(filename)

        if not overwrite and os.path.exists(full_path):
            raise SaveGameException("File already exists. Use 'overwrite=True' to overwrite.")

        try:
            with open(full_path, "w") as fh:
                json.dump(Savegames.to_json(gameboard), fh, indent=4)
        except Exception as err:
            msg = "Error while saving the game: %s" % err
            logging.error(msg)
            raise SaveGameException(msg, original_exception=err)

    @staticmethod
    def load_game(filename: str, reset_players_to_human: bool = False, verbose: Union[bool, int] = False) -> GameBoard:
        """
        Load json file with GameBoard object.

        :param filename: The filename in the ./savegames/ folder to load from.
        :type filename: str
        :param reset_players_to_human: If both players shall be reset to "Human".
        :type reset_players_to_human: bool
        :param verbose: If True, enable verbose logging (default is False, use True or int 0-3).
        :type verbose: Union[bool, int]
        :return: The loaded GameBoard object.
        :rtype: GameBoard
        """
        full_path = Savegames.extend_filename(filename)

        try:
            with open(full_path, "r") as file:
                gb_data = json.load(file)
                gb = Savegames.from_json(gb_data, verbose)
        except FileNotFoundError as err:
            msg = "Could not load file \"%s\"" % filename
            logging.error(msg)
            raise SaveGameException(msg, original_exception=err)
        except Exception as err:
            msg = "An error occurred while loading the game: %s" % err
            logging.error(msg)
            raise SaveGameException(msg, original_exception=err)

        if reset_players_to_human:
            # TODO Skip this if history_pointer does not point to last item
            gb.player_ai[1] = "Human"
            gb.player_ai[2] = "Human"

        return gb

    @staticmethod
    def to_json(gameboard: GameBoard) -> Dict:
        """
        Serialize a GameBoard object into a JSON dictionary.

        :param gameboard: The GameBoard object to be serialized.
        :type gameboard: GameBoard
        :return: The serialized JSON dictionary.
        :rtype: Dict
        """
        return {
            'size_x': gameboard.size_x,
            'size_y': gameboard.size_y,
            'player_ai': gameboard.player_ai,
            'move_history_pointer': gameboard.move_history_pointer,  # Maybe use len(gameboard.move_history) ?
            'move_history': [{
                'x': m.x,
                'y': m.y,
                'h': m.horizontal,
                'p': m.player,
                'a': m.player_ai
            } for m in gameboard.move_history] if len(gameboard.move_history) else []
        }

    @staticmethod
    def from_json(data: Dict, verbose: Union[bool, int] = False) -> GameBoard:
        """
        Deserialize a JSON dictionary into a GameBoard object.

        :param data: The JSON dictionary containing the serialized GameBoard data.
        :type data: Dict
        :param verbose: If True, enable verbose logging (default is False, use True or int 0-3).
        :type verbose: Union[bool, int]
        :return: The deserialized GameBoard object.
        :rtype: GameBoard
        """

        # Read size_x from JSON
        size_x: int = Savegames.enforce_int(
            data.get("size_x", None), 5, 3, 50, context="size_x"
        )

        # Read size_y from JSON
        size_y: int = Savegames.enforce_int(
            data.get("size_y", None), 5, 3, 50, context="size_y"
        )

        gb = GameBoard(
            size_x=size_x,
            size_y=size_y,
            verbose=verbose
        )

        # Read play_ai dict from JSON
        try:
            temp = data.get("player_ai", None)
            player_ai1 = "Human"
            player_ai2 = "Human"
            if temp is None:
                logging.warning("Invalid data in 'player_ai'. Defaulting to Human vs Human.")
            else:
                try:
                    temp1 = temp["1"]
                except KeyError:
                    temp1 = "Human"
                    logging.warning("Invalid data: 'player_ai[1]' not set. Defaulting to Human for player 1.")
                if not temp1 or temp1 not in ['Human', 'RandomAI', 'StupidAI', 'SimpleAI', 'NormalAI', 'BetterAI',
                                              'ClusterAI', 'TreeAI']:
                    logging.warning("Invalid data in 'player_ai[1]'. Defaulting to Human for player 1.")
                else:
                    player_ai1 = temp1
                try:
                    temp2 = temp["2"]
                except KeyError:
                    temp2 = "Human"
                    logging.warning("Invalid data: 'player_ai[2]' not set. Defaulting to Human for player 2.")
                if not temp2 or temp2 not in ['Human', 'RandomAI', 'StupidAI', 'SimpleAI', 'NormalAI', 'BetterAI',
                                              'ClusterAI', 'TreeAI']:
                    logging.warning("Invalid data in 'player_ai[2]'. Defaulting to Human for player 1.")
                else:
                    player_ai2 = temp2
            gb.player_ai = {
                1: player_ai1,
                2: player_ai2
            }
        except Exception as err:
            msg = "Error during deserialization in from_json field player_ai: %s" % err
            logging.error(msg)
            raise SaveGameException(msg, original_exception=err)

        # Read move_history_pointer from JSON
        move_history_pointer = Savegames.enforce_int(
            data.get("move_history_pointer", None), 0, context="move_history_pointer"
        )

        # Read move_history from JSON and make the moves on the gameboard
        try:
            move_history_data = data.get("move_history", None)
            if not isinstance(move_history_data, List) or not all(isinstance(move, Move) for move in move_history_data):
                logging.warning("Invalid data in 'move_history'. Defaulting to empty Gameboard.")
            else:
                for move_data in move_history_data:
                    move = Move(
                        Savegames.enforce_int(move_data.get("x", None), 0, max_value=size_x - 1, context="Move.x"),
                        Savegames.enforce_int(move_data.get("y", None), 0, max_value=size_y - 1, context="Move.y"),
                        Savegames.enforce_int(move_data.get("h", None), 0, max_value=1, context="Move.horizontal"),
                        Savegames.enforce_int(move_data.get("p", None), 1, 1, 2, context="Move.player"),
                        str(move_data.get("a", ""))
                    )
                    gb.make_move(move, print_it=verbose, ignore_current_selected_player=True)
        except Exception as err:
            msg = "Error during deserialization in from_json field move_history: %s" % err
            logging.error(msg)
            raise SaveGameException(msg, original_exception=err)

        # Validate and rewind to move_history_pointer
        len_history = len(gb.move_history)
        if move_history_pointer < len_history:
            for i in range(len_history - move_history_pointer):
                gb.take_back_one_move()
        elif move_history_pointer > len_history:
            logging.warning("Invalid data in 'move_history_pointer'. Defaulting to empty len_history %d."
                            % len_history)
            gb.move_history_pointer = len_history
        else:
            logging.debug("move_history_pointer was just right at the end of the game: %d" % move_history_pointer)

        return gb

    @staticmethod
    def enforce_int(data, default: int = 0, min_value: int = 0, max_value: int = 9999, context: str = "unknown") -> int:
        """
        Ensure that the input data is an integer within the specified range.

        :param data: The input data to be enforced as an integer.
        :param default: The default value to use if data could not be parsed (default is 0).
        :param min_value: The minimum allowed value for the integer (default is 0).
        :param max_value: The maximum allowed value for the integer (default is 9999).
        :param context: A description of the context in which the enforcement is taking place (default is "unknown").
        :return: The enforced integer value.
        :rtype: int
        """
        if max_value < min_value:
            raise SaveGameException(
                "Error in enforce_int: max_value %d must not be smaller then min_value %d in context \"%s\"."
                % (max_value, min_value, context)
            )
        try:
            i = int(data)
            if not isinstance(data, int):
                logging.warning("Value is not an integer, using %d as integer value in context \"%s\"." % (i, context))
        except TypeError:
            logging.warning("Value is not set or cannot be parsed as integer, using default %d in context \"%s\"."
                            % (default, context))
            i = default

        if i < min_value:
            logging.warning("Adjust value %d to its minimal value %d in context \"%s\"." % (i, min_value, context))
            i = min_value
        if i > max_value:
            logging.warning("Adjust value %d to its maximal value %d in context \"%s\"." % (i, max_value, context))
            i = max_value
        return i

    @staticmethod
    def extend_filename(filename: str = "unknown") -> str:
        """
        Extend the given filename with the './savegames/' path if the filename does not contain
        slashes '/' (or '\') and does not start with a dot '.'.

        :param filename: The filename to be extended.
        :type filename: str
        :return: The extended filename.
        :rtype: str
        """

        if not filename or filename.startswith('.') or '/' in filename or '\\' in filename:
            return filename

        save_path = "./savegames/"
        full_path = os.path.join(save_path, filename)

        return full_path
