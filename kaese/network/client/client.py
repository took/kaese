import json
import logging
import queue
import socket
import threading
from time import sleep
from typing import Optional, Union

from kaese.gameboard.box import Box
from kaese.gameboard.gameboard import GameBoard
from kaese.gameboard.move import Move
from kaese.gui.abstract_gui import AbstractGui
from kaese.network.common.Utils import Utils
from kaese.network.messages.client.MoveMsg import MoveMsg
from kaese.network.messages.common.KeepAliveMsg import KeepAliveMsg


class Client:
    """
    Fnord

    The code is documentation enough!
    """

    gui: AbstractGui
    ip: str
    port: int
    verbose: Union[bool, int]

    connection_socket: Optional[socket.socket]

    game_name: str
    gameboard_hash: str

    queue: queue.Queue

    keep_alive_thread: Optional[threading.Thread]
    connection_thread: Optional[threading.Thread]

    def __init__(
            self,
            gui: AbstractGui,
            ip: str = "0.0.0.0",
            port: int = 2345,
            verbose: Union[bool, int] = False
    ) -> None:
        # Get Parameters
        self.gui = gui

        # Optional Parameters
        self.ip = ip
        self.port = port
        self.verbose = verbose

        # Init defaults
        self.connection_socket = None
        self.game_name = ""
        self.gameboard_hash = ""

        # Init Queue
        self.queue = queue.Queue()

        # Log Debug Message
        if self.verbose:
            msg = ("Client initialized with IP: %s Port: %d, starting KeepAlive and Connection thread..."
                   % (self.ip, self.port))
            logging.debug(msg)

        # Start Threads
        self.keep_alive_thread = threading.Thread(target=self._keep_alive_thread)
        self.keep_alive_thread.start()
        self.connection_thread = threading.Thread(target=self._connection_thread)
        self.connection_thread.start()

    def _keep_alive_thread(self) -> None:
        """Keeps putting a KeepAliveMsg on the Queue every 5 seconds"""

        self.gui.running = True  # TODO Refactor to "killed" instead!

        if self.verbose > 2:
            logging.debug("Client keep_alive_thread: started")

        while self.gui.running:  # TODO Refactor to "killed" instead!
            sleep(5)
            if self.ip is not None and self.connection_socket:
                keep_alive_msg = KeepAliveMsg()
                self.queue.put(keep_alive_msg)

    def _connection_thread(self) -> None:
        """(Re-)connects to the server and reads Msgs from the socket to write them to the queue"""

        self.gui.running = True  # TODO Refactor to "killed" instead!

        if self.verbose > 2:
            logging.debug("Client connection_thread: started")

        while self.gui.running:  # TODO Refactor to "killed" instead!
            if self.ip is None:
                sleep(1)
                continue
            if self.connection_socket is None:
                msg = ("Client connection_thread: Connecting to %s:%d" % (self.ip, self.port))
                logging.info(msg)
                try:
                    self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # self.connection_socket.settimeout(10)  # Implement KeepAlive before using this
                    self.connection_socket.connect((self.ip, self.port))
                except Exception as e:
                    logging.error(
                        "Client connection_thread: Error connecting to %s:%d: %s" % (self.ip, self.port, str(e)))
                    self.connection_socket = None
                    sleep(15)
                    continue
            if self.connection_socket:
                # TODO Add timeout or make non-blocking to allow seamless shutdown of app
                #  when self.gui.running becomes False (or self.gui.killed becomes True).
                #
                #  Implement fully working KeepAlive before implementing this.
                #
                #  Maybe this is not needed since we can shutdown with sys.exit()?
                #  Then, we should keep the behaviour without the timeout, that an empty message shall result in
                #  a disconnect (If not message: -> "Lost Connection").
                #
                # Example (use together with self.connection_socket.settimeout(3)):
                #   try:
                #       rec = self.connection_socket.recv(2048)  # try to receive 2048 bytes
                #   except socket.timeout:  # fail after 3 second of no activity
                #       print("Didn't receive data! [Timeout]")
                #   finally:
                #       s.close()
                message = self.connection_socket.recv(2048)  # May raise ConnectionResetError, ...
                if message:
                    print(message)
                    json_objects = message.decode().strip().split("\n")
                    for json_object in json_objects:
                        try:
                            msg_obj = json.loads(json_object.strip(), object_hook=Utils.object_decoder_for_client)
                            print(msg_obj)
                            if msg_obj is not None:
                                self.queue.put(msg_obj)
                                if self.verbose > 2:
                                    logging.debug("Client connection_thread: Queued received Message")
                        except json.JSONDecodeError as e:
                            logging.error("Client connection_thread: Error decoding JSON: %s (%s)",
                                          (str(e), json_object))
                else:
                    logging.info("Client connection_thread: Lost Connection")
                    self.connection_socket = None
                    sleep(3)

    def gui_hook_handle_network(self) -> bool:
        """
        Needs to be called from Gui regularly to handle the Queue.

        :return: returns True if redraw is needed, False otherwise
        """

        # Empty Queue if no IP is configured (yet or anymore)
        if self.ip is None:
            while True:
                try:
                    self.queue.get(False)
                except queue.Empty:
                    break
            return False

        # Read and process all Messages from the Queue.
        # Return True if any of those events set redraw = True.
        # TODO Maybe add logic to prevent to block too long with lots of Messages. Set a max of messages
        #   per run or even measure the time already elapsed.
        redraw = False
        while True:
            # Read Messages from Queue until Queue is empty
            try:
                msg_obj = self.queue.get(False)
            except queue.Empty:
                break

            # Handle incoming Messages
            if msg_obj.message_type == 'ChatMsg':
                msg = msg_obj.text.strip()
                context = msg_obj.context.strip()
                print("-> Server Chat: " + msg.replace("\n", "\\n"))
                logging.debug("Client gui_hook_handle_network in: Received Server Chat: " + msg.replace("\n", "\\n"))
                self.gui.popup_info(msg, context, "default")  # TODO Improve Chat features
                redraw = True

            elif msg_obj.message_type == 'KeepAliveMsg':
                if self.verbose > 2:
                    logging.debug("Client gui_hook_handle_network in: Received KeepAlive")
                # self.keep_alive_received = time.time()
                # redraw = True

            elif msg_obj.message_type == 'GameStateMsg':
                if self.verbose > 1:
                    msg = "Client gui_hook_handle_network in: GameState received"
                    logging.info(msg)
                    print("-> " + msg)
                player = msg_obj.for_player
                self.game_name = msg_obj.game_name
                self.gameboard_hash = msg_obj.gameboard_hash

                self.gui.gb = GameBoard(msg_obj.size_x, msg_obj.size_y, self.verbose)
                self.gui.gb.boxes = []
                for x in range(self.gui.gb.size_x):
                    column = []
                    for y in range(self.gui.gb.size_y):
                        box = msg_obj.boxes[x][y]
                        column.append(Box(box[0], box[1], box[2]))
                    self.gui.gb.boxes.append(column)
                self.gui.gb.win_counter = msg_obj.win_counter
                self.gui.gb.moves_made = msg_obj.moves_made
                self.gui.gb.remaining_moves = msg_obj.remaining_moves
                self.gui.gb.current_player = msg_obj.current_player
                self.gui.gb.player_ai = {
                    1: msg_obj.player_ai[1],
                    2: msg_obj.player_ai[2]
                }
                self.gui.gb.player_ai[player] = "Human"  # A bit of a dirty hack here...
                self.gui.gb.winner = msg_obj.winner
                self.gui.gb.win_counter = {
                    1: msg_obj.win_counter[1],
                    2: msg_obj.win_counter[2]
                }
                # self.gui.gb.last_move = msg_obj.last_move
                # self.gui.gb.move_history = msg_obj.move_history
                self.gui.gb.move_history_pointer = msg_obj.move_history_pointer

                redraw = True

            elif msg_obj.message_type == 'InvalidMoveMsg':
                # Write error message using logging, STDOUT and PopUp window
                err = msg_obj.error_message.strip()
                msg = "Client gui_hook_handle_network in: InvalidMoveMsg received: " + err
                logging.error(msg)
                print("-> " + msg)
                self.gui.popup_info(err, "Invalid Move")  # TODO color_set "error"
                redraw = True

            elif msg_obj.message_type == 'WelcomeMsg':
                if self.verbose:
                    msg = "Client gui_hook_handle_network in: Welcome received"
                    logging.info(msg)
                    print("-> " + msg)
                self.gui.popup_info("Connected to %s:%d" % (self.ip, self.port), "Connected")
                redraw = True

            # Handle outgoing Messages
            # TODO Refactor Move these to own Queue and Thread
            elif msg_obj.message_type == 'MoveMsg':
                # Send MoveMsg to server
                self.connection_socket.send(Utils.object_encoder_adv(msg_obj))

            elif msg_obj.message_type == 'KeepAliveMsg':
                # Send KeepAliveMsg to server
                self.connection_socket.send(Utils.object_encoder_adv(msg_obj))

        return redraw

    def gui_hook_queue_move_for_sending(self, move: Move) -> None:
        """
        Enqueues a MoveMsg instance to self.queue() to be sent to the server.

        This method shall be called from the GUI whenever the local player makes a move.

        Args:
            move (Move): An object representing the player's move, which contains
                         the move's coordinates (x, y) and direction (horizontal).
        """
        move_msg = MoveMsg(self.game_name, self.gameboard_hash, move.x, move.y, move.horizontal)
        self.queue.put(move_msg)
