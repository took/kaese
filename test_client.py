import json
import select
import socket
import sys
from _thread import *
from time import sleep

from kaese.ai.ai_exception import AIException
from kaese.ai.normal_ai import NormalAI
from kaese.gameboard.box import Box
from kaese.gameboard.gameboard import GameBoard
from kaese.gameboard.move import Move
from kaese.network.common.Utils import Utils
from kaese.network.messages.client.MoveMsg import MoveMsg
from kaese.network.messages.common.ChatMsg import ChatMsg
from kaese.network.messages.common.KeepAliveMsg import KeepAliveMsg


def keep_alive_thread(delay):
    while running:
        sleep(delay)
        print("Ping")
        keep_alive = KeepAliveMsg()
        server.send(Utils.object_encoder_adv(keep_alive))


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_address = str('127.0.0.1')
Port = int(2345)
server.connect((IP_address, Port))

start_new_thread(keep_alive_thread, (5, ))

verbose = False
gb = None
player = 0
game_name = ""
gameboard_hash = ""

running = True
while running:

    # maintains a list of possible input streams
    # This will fail on Windows OS, since stdin can not be used like a socket in Windows.
    sockets_list = [sys.stdin, server]

    """ There are two possible input situations. Either the 
    user wants to give manual input to send to other people, 
    or the server is sending a message to be printed on the 
    screen. Select returns from sockets_list, the stream that 
    is reader for input. So for example, if the server wants 
    to send a message, then the if condition will hold true 
    below. If the user wants to send a message, the else 
    condition will evaluate as true"""
    read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)  # May raise ConnectionResetError, ...
            if message:
                print(message)
                json_objects = message.decode().strip().split("\n")
                for json_object in json_objects:
                    try:
                        msg_obj = json.loads(json_object.strip(), object_hook=Utils.object_decoder_for_client)
                        print(msg_obj)
                        if msg_obj is not None:
                            if msg_obj.message_type == 'ChatMsg':
                                print("-> Server Chat: " + msg_obj.text.strip())
                            if msg_obj.message_type == 'KeepAliveMsg':
                                print("-> KeepAlive received")
                            if msg_obj.message_type == 'GameStateMsg':
                                print("-> GameState received")
                                player = msg_obj.for_player
                                game_name = msg_obj.game_name
                                gameboard_hash = msg_obj.gameboard_hash
                                gb = GameBoard(msg_obj.size_x, msg_obj.size_y, verbose)
                                gb.boxes = []
                                for x in range(gb.size_x):
                                    column = []
                                    for y in range(gb.size_y):
                                        box = msg_obj.boxes[x][y]
                                        column.append(Box(box[0], box[1], box[2]))
                                    gb.boxes.append(column)
                                gb.win_counter = msg_obj.win_counter
                                gb.moves_made = msg_obj.moves_made
                                gb.remaining_moves = msg_obj.remaining_moves
                                gb.current_player = msg_obj.current_player
                                gb.player_ai = msg_obj.player_ai
                                gb.winner = msg_obj.winner
                                gb.win_counter = msg_obj.win_counter
                                # gb.last_move = msg_obj.last_move
                                # gb.move_history = msg_obj.move_history
                                gb.move_history_pointer = msg_obj.move_history_pointer
                            if msg_obj.message_type == 'InvalidMoveMsg':
                                print("-> InvalidMove received: " + msg_obj.error_message.strip())
                            if msg_obj.message_type == 'WelcomeMsg':
                                print("-> Welcome received")

                    except json.JSONDecodeError as e:
                        print("Error decoding JSON: %s (%s)", (str(e), json_object))
            else:
                print("Lost Connection")
                running = False
        else:
            message = sys.stdin.readline().strip()

            if message == 'move':
                if gb:
                    ki = NormalAI()
                    try:
                        move = ki.get_next_move(gb, player)
                        msg_obj = MoveMsg(game_name, gameboard_hash, move.x, move.y, move.horizontal)
                        server.send(Utils.object_encoder_adv(msg_obj))
                    except AIException as e:
                        print("It is not your turn!")
                else:
                    print("No game running!")
            else:
                msg_obj = ChatMsg(message)
                server.send(Utils.object_encoder_adv(msg_obj))

                sys.stdout.write("<You> ")
                sys.stdout.write(message)
                sys.stdout.flush()

server.close()
sys.exit()
