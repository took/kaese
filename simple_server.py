import _queue
import json
import queue
import socket
import sys
from _thread import *
from time import sleep
from typing import Optional, Tuple

from kaese.gameboard.gameboard import GameBoard
from kaese.gameboard.invalid_move_exception import InvalidMoveException
from kaese.gameboard.move import Move
from kaese.network.common.Utils import Utils
from kaese.network.messages.common.KeepAliveMsg import KeepAliveMsg
from kaese.network.messages.Message import Message
from kaese.network.messages.common.ChatMsg import ChatMsg
from kaese.network.messages.client.MoveMsg import MoveMsg
from kaese.network.messages.server.GameStateMsg import GameStateMsg
from kaese.network.messages.server.InvalidMoveMsg import InvalidMoveMsg
from kaese.network.messages.server.WelcomeMsg import WelcomeMsg
from kaese.network.messages.server.local.ClientDisconnectMsg import ClientDisconnectMsg
from kaese.network.messages.server.local.InternalMoveMsg import InternalMoveMsg
from kaese.network.messages.server.local.NewGameMsg import NewGameMsg


class SimpleServer:
    game_name: str
    size_x: int
    size_y: int
    gameboard: GameBoard
    player_1: str
    player_2: str

    is_killed: bool
    manager_queue: queue.Queue
    client_1_queue: queue.Queue
    client_2_queue: queue.Queue

    connection_client_1: Optional[Tuple[any, Tuple[str, int]]]
    connection_client_2: Optional[Tuple[any, Tuple[str, int]]]

    def __init__(self, client_connections=None) -> None:
        self.game_name = "Network Game"  # Use different name for each game if a server is able to handle several games
        self.size_x = 8
        self.size_y = 5
        self.gameboard = None
        self.player_1 = 'Client_1'
        self.player_2 = 'Client_2'

        self.is_killed = False
        self.manager_queue = queue.Queue()
        self.client_1_queue = queue.Queue()
        self.client_2_queue = queue.Queue()

        self.connection_client_1 = None
        self.connection_client_2 = None
        if client_connections is not None:
            self.connection_client_1 = client_connections[0]
            self.connection_client_2 = client_connections[1]

    def main(self):
        start_new_thread(self.local_terminal_thread, ())
        start_new_thread(self.manager_thread, ())
        if self.connection_client_1 is None or self.connection_client_2 is None:
            start_new_thread(self.server_thread, ())

        while not self.is_killed:
            sleep(1)
        sys.exit()

    def local_terminal_thread(self):
        # Read Admin Commands from local Keyboard
        while not self.is_killed:
            line = input().strip()
            if line == 'help':
                print("~ Help:")
                print("~  help: This help text")
                print("~  start: (Re-)start game")
                print("~  exit: Shutdown")
            elif line == 'start':
                print("~ (Re-)start game")
                new_game_msg = NewGameMsg(self.game_name, self.size_x, self.size_y)
                self.manager_queue.put(new_game_msg)
            elif line == 'exit':
                print("~ Shutdown")
                self.is_killed = True
            else:
                print("~ Unknown command, type \"help\" for help")

        print("Exit Local-Terminal-Thread")
        sys.exit()

    def manager_thread(self):
        # Handles the game logic
        verbose = True
        game_running = False
        while not self.is_killed:
            if self.connection_client_1 and self.connection_client_2:
                if not game_running:
                    game_running = True
                    new_game_msg = NewGameMsg(self.game_name, self.size_x, self.size_y)
                    self.manager_queue.put(
                        new_game_msg)  # TODO Send game state instead if an old game is still avail to reconnect to

            msg_obj = None
            try:
                msg_obj = self.manager_queue.get(True, 1.5)
            except queue.Empty:
                # Ignore empty queue exception
                pass
            if msg_obj:
                if msg_obj.message_type == 'NewGameMsg':
                    print("Manage NewGameMsg")
                    self.gameboard = GameBoard(msg_obj.size_x, msg_obj.size_y, verbose)

                    gs_msg_player_1 = GameStateMsg(1, msg_obj.game_name, self.gameboard)
                    self.client_1_queue.put(gs_msg_player_1)
                    gs_msg_player_2 = GameStateMsg(2, msg_obj.game_name, self.gameboard)
                    self.client_2_queue.put(gs_msg_player_2)

                elif msg_obj.message_type == 'InternalMoveMsg':
                    print("Manage InternalMoveMsg")

                    if not msg_obj.game_name == self.game_name:
                        self.queue_invalid_move_msg(msg_obj.client_id, "Game Name does not match")
                        continue
                    gs_msg = GameStateMsg(1, msg_obj.game_name, self.gameboard)  # TODO Refactor: Move hash fct
                    if not msg_obj.gameboard_hash == gs_msg.gameboard_hash:
                        self.queue_invalid_move_msg(msg_obj.client_id, "Gameboard Hash does not match")
                        continue
                    if self.player_1 == 'Client_1':
                        if not msg_obj.client_id == self.gameboard.current_player:
                            self.queue_invalid_move_msg(msg_obj.client_id, "Wrong Player")
                            continue
                    elif self.player_2 == 'Client_1':
                        if msg_obj.client_id == self.gameboard.current_player:
                            self.queue_invalid_move_msg(msg_obj.client_id, "Wrong Player")
                            continue

                    move = Move(msg_obj.x, msg_obj.y, msg_obj.horizontal, self.gameboard.current_player)
                    try:
                        self.gameboard.make_move(move, False, False, True)
                    except InvalidMoveException as e:
                        self.queue_invalid_move_msg(msg_obj.client_id, str(e))
                        continue

                    gs_msg_player_1 = GameStateMsg(1, msg_obj.game_name, self.gameboard)
                    self.client_1_queue.put(gs_msg_player_1)
                    gs_msg_player_2 = GameStateMsg(2, msg_obj.game_name, self.gameboard)
                    self.client_2_queue.put(gs_msg_player_2)

                elif msg_obj.message_type == 'ClientDisconnectMsg':
                    print("Manage ClientDisconnectMsg")
                    game_running = False
                    # TODO Send chat message to other client...
                else:
                    print("Unknown Message type in Manager-Queue")

        print("Exit Manager-Thread")

    def queue_invalid_move_msg(self, client_id, err_msg):
        invalid_move_msg = InvalidMoveMsg(err_msg)
        if client_id == 1:
            q = self.client_1_queue
        else:
            q = self.client_2_queue
        q.put(invalid_move_msg)

    def server_thread(self):
        # Accepts new connections
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ip_address = str('0.0.0.0')
        port = int(2345)
        server.bind((ip_address, port))
        server.listen(2)

        # print(server.getsockname())

        while not self.is_killed:
            sock, addr = server.accept()
            if self.connection_client_1 is None:
                self.connection_client_1 = (sock, addr)
                print("First Client connected from: " + addr[0] + ":" + str(addr[1]))
                start_new_thread(self.client_output_thread, (1, sock, addr))
                start_new_thread(self.client_input_thread, (1, sock, addr))
            elif self.connection_client_2 is None:
                self.connection_client_2 = (sock, addr)
                print("Second Client connected from: " + addr[0] + ":" + str(addr[1]))
                start_new_thread(self.client_output_thread, (2, sock, addr))
                start_new_thread(self.client_input_thread, (2, sock, addr))
            else:
                print("Too many clients from: " + addr[0] + ":" + str(addr[1]))
                sock.close()

        server.close()

        print("Exit Server-Thread")

    def client_output_thread(self, client_id: int, sock: socket, addr: Tuple[str, int]):
        # Send Messages to Clients
        if client_id == 1:
            q = self.client_1_queue  # sock = self.connection_client_1[0]  # addr = self.connection_client_1[1]
        else:
            q = self.client_2_queue  # sock = self.connection_client_2[0]  # addr = self.connection_client_2[1]
        while not self.is_killed:
            if client_id == 1:
                if not self.connection_client_1:
                    break
            else:
                if not self.connection_client_2:
                    break
            msg_obj = None
            try:
                msg_obj = q.get(True, 3)
            except _queue.Empty:
                # Ignore Empty Queue
                pass
            if msg_obj:
                if msg_obj.message_type == 'ChatMsg':
                    print("Send ChatMsg to Client " + str(client_id))
                    self.send_message_object(client_id, msg_obj)
                elif msg_obj.message_type == 'KeepAliveMsg':
                    print("Send KeepAliveMsg to Client " + str(client_id))
                    self.send_message_object(client_id, msg_obj)
                elif msg_obj.message_type == 'GameStateMsg':
                    print("Send GameStateMsg to Client " + str(client_id))
                    self.send_message_object(client_id, msg_obj)
                elif msg_obj.message_type == 'InvalidMoveMsg':
                    print("Send InvalidMoveMsg to Client " + str(client_id))
                    self.send_message_object(client_id, msg_obj)
                elif msg_obj.message_type == 'WelcomeMsg':
                    print("Send WelcomeMsg to Client " + str(client_id))
                    self.send_message_object(client_id, msg_obj)
                else:
                    print("Unknown Message Type in Client-Output-Thread: " + msg_obj.message_type)
                    print(msg_obj)

        print(
            "Exit Client-Output-Thread Player " + str(client_id) + " for Client from: " + addr[0] + ":" + str(addr[1]))

    def client_input_thread(self, client_id: int, sock: socket, addr: Tuple[str, int]):
        if client_id == 1:
            # sock = self.connection_client_1[0]
            q = self.client_1_queue
        else:
            # sock = self.connection_client_2[0]
            q = self.client_2_queue

        # Receives messages from Client
        welcome_msg = WelcomeMsg()
        self.send_message_object(client_id, welcome_msg)  # TODO Put in Queue instead of sync sending here

        player = client_id
        chat_msg = ChatMsg("Welcome to the lobby Client " + str(client_id) + "!\nYou are Player " + str(player))
        self.send_message_object(client_id, chat_msg)  # TODO Put in Queue instead of sync sending here

        while not self.is_killed:
            msg_obj = self.get_message_object(client_id)
            if msg_obj is None:
                break
            # print(type(msg_obj))
            # print(msg_obj)
            if msg_obj.message_type == 'MoveMsg':
                internal_move_msg = InternalMoveMsg(client_id, msg_obj.game_name, msg_obj.gameboard_hash, msg_obj.x,
                                                    msg_obj.y, msg_obj.horizontal)
                self.manager_queue.put(internal_move_msg)
            elif msg_obj.message_type == 'ChatMsg':
                print("Client " + str(client_id) + " (Player " + str(player) + ") said: " + msg_obj.text.strip())
            elif msg_obj.message_type == 'KeepAliveMsg':
                print("Ping from Client " + str(client_id) + " (Player " + str(player) + ")")
                keep_alive = KeepAliveMsg()
                q.put(keep_alive)
            else:
                print("Unknown Message Type in Client-Input-Thread")
                print(msg_obj)

        print("Exit Client-Input-Thread Client " + str(client_id) + " (Player " + str(player) + ") for Client from: " +
              addr[0] + ":" + str(addr[1]))

    def send_message_object(self, client_id: int, msg_obj: Message):
        try:
            if client_id == 1:
                sock = self.connection_client_1[0]
            else:
                sock = self.connection_client_2[0]
            sock.send(Utils.object_encoder_adv(msg_obj))
        except Exception as e:
            self.remove_connection(client_id, "Exception while sending Message to Client " + str(client_id), e)

    def get_message_object(self, client_id: int) -> Optional[Message]:
        try:
            if client_id == 1:
                sock = self.connection_client_1[0]
            else:
                sock = self.connection_client_2[0]
            message = sock.recv(2048)
            if message:
                # TODO Refactor Network - json_object.strip()
                # Split message by linebreak and handle more than on message or fill up a buffer with unprocessed parts
                obj = json.loads(message.decode())
                if obj is not None:
                    msg_obj = Utils.object_decoder_for_server(obj)
                    if msg_obj is not None:
                        return msg_obj
                self.remove_connection(client_id, "Received invalid Message from Client " + str(client_id))
                return None
            else:
                self.remove_connection(client_id, "Received empty Message from Client " + str(client_id))
                return None
        except Exception as e:
            self.remove_connection(client_id, "Exception while receiving Message from Client " + str(client_id), e)
            return None

    def remove_connection(self, client_id: int, reason: str, exception: Exception = None):
        # TODO Refactor me!
        if client_id == 1:
            if self.connection_client_1 is None:
                # Return early if Player 1 is already recognized as disconnected
                return None
            # Set sock and addr to Client 1
            sock = self.connection_client_1[0]
            addr = self.connection_client_1[1]
        else:
            if self.connection_client_2 is None:
                # Return early if Player 2 is already recognized as disconnected
                return None
            # Set sock and addr to Client 2
            sock = self.connection_client_2[0]
            addr = self.connection_client_2[1]

        # Output (Debug-)Message (TODO Write to log instead)
        print("Remove Client " + str(client_id) + " from " + addr[0] + ":" + str(addr[1]) + ": " + reason)
        if exception is not None:
            print(exception)

        # Mark Client as Disconnected and close Socket if not already disconnected
        if self.connection_client_1 is not None and self.connection_client_1[0] == sock:
            self.connection_client_1 = None
            sock.close()
            if self.connection_client_2 is not None:
                chat_msg = ChatMsg("Client 1 disconnected. Please wait for reconnect...")
                self.client_2_queue.put(chat_msg)
        elif self.connection_client_2 is not None and self.connection_client_2[0] == sock:
            self.connection_client_2 = None
            sock.close()
            if self.connection_client_1 is not None:
                chat_msg = ChatMsg("Client 2 disconnected. Please wait for reconnect...")
                self.client_1_queue.put(chat_msg)

        # Put ClientDisconnectMsg on Queue to inform the manager_thread about the Event
        client_disconnect_msg = ClientDisconnectMsg(client_id)
        self.manager_queue.put(client_disconnect_msg)


if __name__ == "__main__":
    s = SimpleServer()
    s.main()
