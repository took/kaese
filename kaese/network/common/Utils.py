import json

from kaese.network.messages.Message import Message
from kaese.network.messages.client.MoveMsg import MoveMsg
from kaese.network.messages.common.ChatMsg import ChatMsg
from kaese.network.messages.common.KeepAliveMsg import KeepAliveMsg
from kaese.network.messages.server.GameStateMsg import GameStateMsg
from kaese.network.messages.server.InvalidMoveMsg import InvalidMoveMsg
from kaese.network.messages.server.WelcomeMsg import WelcomeMsg


class Utils:
    object_decoder_for_server = None
    object_decoder_for_client = None
    object_encoder = None

    @staticmethod
    def object_decoder_for_server(obj):
        """
        Decode Messages that Servers receives. Use after obj = json.loads(message.decode()).

        Example usage:
            message = sock.recv(2048)
            if message:
                obj = json.loads(message.decode())
                if obj is not None:
                    msg_obj = Utils.object_decoder_for_server(obj)

        :param obj:
        :return:
        """
        if 'message_type' in obj:
            if obj['message_type'] == 'ChatMsg':
                return ChatMsg(obj['text'], obj['context'])
            if obj['message_type'] == 'KeepAliveMsg':
                return KeepAliveMsg()
            if obj['message_type'] == 'MoveMsg':
                return MoveMsg(obj['game_name'], obj['gameboard_hash'], obj['x'], obj['y'], obj['horizontal'])
        return None

    @staticmethod
    def object_decoder_for_client(obj):
        """
        Decode Messages that Clients receives. To be used together with json.loads().

        Example usage:
            message = self.connection.recv(2048)
            print(message)
            json_objects = message.decode().strip().split("\n")
            for json_object in json_objects:
                try:
                    msg_obj = json.loads(json_object.strip(), object_hook=Utils.object_decoder_for_client)
                    print(msg_obj)
                        if msg_obj is not None:
                            self.queue.put(msg_obj)

        :param obj:
        :return:
        """
        if 'message_type' in obj and obj['message_type'] == 'ChatMsg':
            return ChatMsg(obj['text'], obj['context'])
        if 'message_type' in obj and obj['message_type'] == 'KeepAliveMsg':
            return KeepAliveMsg()
        if 'message_type' in obj and obj['message_type'] == 'GameStateMsg':
            gs_msg = GameStateMsg(obj['for_player'], obj['game_name'])
            gs_msg.size_x = obj['size_x']
            gs_msg.size_y = obj['size_y']
            gs_msg.boxes = obj['boxes']
            gs_msg.current_player = obj['current_player']
            gs_msg.player_ai = {1: obj['player_ai_1'], 2: obj['player_ai_2']}
            gs_msg.winner = obj['winner']
            gs_msg.win_counter = {1: obj['win_counter_1'], 2: obj['win_counter_2']}
            gs_msg.moves_made = obj['moves_made']
            gs_msg.remaining_moves = obj['remaining_moves']
            # gs_msg.last_move = None
            # gs_msg.move_history = None
            gs_msg.move_history_pointer = obj['move_history_pointer']
            gs_msg.gameboard_hash = obj['gameboard_hash']
            return gs_msg
        if 'message_type' in obj and obj['message_type'] == 'InvalidMoveMsg':
            return InvalidMoveMsg(obj['error_message'])
        if 'message_type' in obj and obj['message_type'] == 'WelcomeMsg':
            return WelcomeMsg()
        return None

    @staticmethod
    def object_encoder(obj):
        """
        Encode a message object to a dictionary.

        This method takes an object that supports the `_asdict` method and returns its dictionary representation.

        Example usage:
            msg_obj = KeepAliveMsg()
            server_or_client_connection.send(json.dumps(msg_obj, default=Utils.object_encoder).encode())

        :param obj: The object to be encoded, which must have an `_asdict` method.
        :return: The dictionary representation of the object.
        """
        return obj._asdict()

    @staticmethod
    def object_encoder_adv(msg_obj: Message):
        """
        Encode a Message object to a JSON string and then to bytes.

        This method converts a Message object into a JSON string, appends a newline character,
        and encodes the result as bytes. The Message object must support the `_asdict` method.

        Example usage:
            msg_obj = KeepAliveMsg()
            server_or_client_connection.send(Utils.object_encoder_adv(msg_obj))

        :param msg_obj: The Message object to be encoded.
        :return: The byte-encoded JSON string representation of the object, with a newline character appended.
        """
        return (json.dumps(msg_obj, default=Utils.object_encoder) + "\n").encode()
