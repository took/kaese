from typing import Dict, Any, List, Optional
import pickle
import tkinter
import tkinter.filedialog as tk_file_dialog
import tkinter.messagebox as tk_message_box

from datetime import datetime
from typing import List, Optional, Any, Union

import logging
# import threading

import kaese.ai.better_ai
import kaese.ai.cluster_ai
import kaese.ai.normal_ai
import kaese.ai.random_ai
import kaese.ai.simple_ai
import kaese.ai.stupid_ai
import kaese.ai.tree_ai
from kaese.gameboard.gameboard import GameBoard
from kaese.gameboard.move import Move
from kaese.gui.abstract_gui import AbstractGui
from kaese.gui.themes.theme import Theme
from kaese.savegames.savegames import Savegames


class TkinterGui(AbstractGui):  # TODO Vielleicht sollte man die AbstractGui garnicht vererben für TKInter?
    gb: GameBoard
    screen_width: int
    screen_height: int
    tree_ai_max_moves: int
    verbose: Union[bool, int]

    gb_size_x: int
    gb_size_y: int
    master: tkinter.Tk
    canvas: tkinter.Canvas
    player_messages: tkinter.Text
    next_player_color_field: tkinter.Canvas
    next_player_color_field_rectangle: Any
    line_distance: int
    player_colors: List[str]
    line_widgets_to_move: Dict[Any, Move]
    coords_to_line_widgets: Dict[Any, Any]
    player_ai: Dict[int, tkinter.StringVar]
    recent_filename: Optional[str]
    canvas_width: int
    canvas_height: int

    def __init__(
            self,
            theme: Theme,
            gb_size_x: int,
            gb_size_y: int,
            ai_interval: int = 2000,
            player1: str = "Human",
            player2: str = "Human",
            tree_ai_max_moves: int = 8,
            verbose: Union[bool, int] = False
    ) -> None:
        # Get Parameters
        self.theme = theme
        self.ai_interval = ai_interval
        self.player1 = player1
        self.player2 = player2
        self.tree_ai_max_moves = tree_ai_max_moves
        self.verbose = verbose

        # Init Gameboard
        self.gb_size_x = gb_size_x
        self.gb_size_y = gb_size_y
        self.gb = GameBoard(gb_size_x, gb_size_y, self.verbose)
        self.gb.player_ai = {
            1: player1,
            2: player2
        }

        # Init self.recent_filename
        self.recent_filename = None

        # Init empty self.line_widgets_to_move and coords_to_line_widgets
        self.line_widgets_to_move = {}
        self.coords_to_line_widgets = {}

        # Init running state
        # self.ai_timer = 0
        # self.ai_thread = None
        # self.ai_thread_start_time = None
        # self.running_tree_ai = None
        # self.tree_ai_move = None

        # distance (in pixels) of the lines on the spielfeld...
        self.line_distance = 75
        if self.line_distance * self.gb.size_x > 500 or self.line_distance * self.gb.size_y > 500:
            self.line_distance = int(500 / max(self.gb.size_x, self.gb.size_y))
            if self.line_distance < 20:
                self.line_distance = 20

        self.player_colors = ["grey", "red", "green", "black"]  # none, Player1, Player2, "System" (cur. unused)
        self.player_ai = {}  # 1: "Human", 2: "SimpleAI" for example

        self.master = tkinter.Tk()
        # self.master.geometry('+100+100')
        # self.master.resizable(width=False, height=False)
        self.master.wm_title("Käsekästchen")
        self.canvas_width = self.gb.size_x * self.line_distance
        self.canvas_height = self.gb.size_y * self.line_distance
        self.canvas = tkinter.Canvas(self.master, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()
        self.player_messages = tkinter.Text(self.master, height=2, width=65)
        self.player_messages.pack(side=tkinter.LEFT, fill=tkinter.Y)
        self.next_player_color_field = tkinter.Canvas(self.master, width=25, height=10)
        self.next_player_color_field_rectangle = self.next_player_color_field.create_rectangle(3, 3, 22, 22,
                                                                                               fill=self.player_colors[
                                                                                                   1])
        self.next_player_color_field.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        self.player_ai[1] = tkinter.StringVar()
        self.player_ai[1].set("Human")
        self.player_ai[2] = tkinter.StringVar()
        self.player_ai[2].set("Human")

        menubar = tkinter.Menu(self.master)

        file_menu = tkinter.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Game", command=self.menu_new_game)
        file_menu.add_separator()
        file_menu.add_command(label="Open", command=self.menu_load_game)
        file_menu.add_command(label="Save", command=self.menu_save_game)
        file_menu.add_command(label="Save as...", command=self.menu_save_game_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        player1menu = tkinter.Menu(menubar, tearoff=0)
        player1menu.add_radiobutton(variable=self.player_ai[1], command=self.menu_set_player1, label="Human",
                                    value="Human")
        player1menu.add_separator()
        player1menu.add_radiobutton(variable=self.player_ai[1], command=self.menu_set_player1, label="Stupid Ki",
                                    value="StupidAI")
        player1menu.add_radiobutton(variable=self.player_ai[1], command=self.menu_set_player1, label="Random Ki",
                                    value="RandomAI")
        player1menu.add_radiobutton(variable=self.player_ai[1], command=self.menu_set_player1, label="Simple Ki",
                                    value="SimpleAI")
        player1menu.add_radiobutton(variable=self.player_ai[1], command=self.menu_set_player1, label="Normal Ki",
                                    value="NormalAI")
        player1menu.add_radiobutton(variable=self.player_ai[1], command=self.menu_set_player1, label="Better Ki",
                                    value="BetterAI")
        player1menu.add_radiobutton(variable=self.player_ai[1], command=self.menu_set_player1, label="Cluster Ki",
                                    value="ClusterAI")
        player1menu.add_radiobutton(variable=self.player_ai[1], command=self.menu_set_player1, label="Baum Ki",
                                    value="TreeAI")
        menubar.add_cascade(label="Player 1", menu=player1menu, background=self.player_colors[1],
                            activebackground=self.player_colors[1])

        player2menu = tkinter.Menu(menubar, tearoff=0)
        player2menu.add_radiobutton(variable=self.player_ai[2], command=self.menu_set_player2, label="Human",
                                    value="Human")
        player2menu.add_separator()
        player2menu.add_radiobutton(variable=self.player_ai[2], command=self.menu_set_player2, label="Stupid Ki",
                                    value="StupidAI")
        player2menu.add_radiobutton(variable=self.player_ai[2], command=self.menu_set_player2, label="Random Ki",
                                    value="RandomAI")
        player2menu.add_radiobutton(variable=self.player_ai[2], command=self.menu_set_player2, label="Simple Ki",
                                    value="SimpleAI")
        player2menu.add_radiobutton(variable=self.player_ai[2], command=self.menu_set_player2, label="Normal Ki",
                                    value="NormalAI")
        player2menu.add_radiobutton(variable=self.player_ai[2], command=self.menu_set_player2, label="Better Ki",
                                    value="BetterAI")
        player2menu.add_radiobutton(variable=self.player_ai[2], command=self.menu_set_player2, label="Cluster Ki",
                                    value="ClusterAI")
        player2menu.add_radiobutton(variable=self.player_ai[2], command=self.menu_set_player2, label="Baum Ki",
                                    value="TreeAI")
        menubar.add_cascade(label="Player 2", menu=player2menu, background=self.player_colors[2],
                            activebackground=self.player_colors[2])

        help_menu = tkinter.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Help", command=self.menu_help)
        help_menu.add_command(label="Spielregeln", command=self.menu_help_spielregeln)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.menu_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.master.config(menu=menubar)

        self.render_gameboard(self.gb)
        self.player_messages.insert(tkinter.CURRENT, "Game started. Player 1 up.\nViel Erfolg!\n")

        self.master.after(2000, self.check_ki)

        msg = ("Tkinter-GUI initialized, Next Up: Player %d (%s)"
               % (self.gb.current_player, self.gb.player_ai[self.gb.current_player]))
        logging.debug(msg)

    def make_move(self, move: Move) -> None:
        """Make move on gb and redraw gameboard"""
        if self.gb.move_history_pointer != len(self.gb.move_history):
            # Deny move
            return
        self.gb.make_move(move)
        self.gb.last_move = Move(move.x, move.y, move.horizontal, move.player, move.player_ai)
        self.check_game_state()

        # TKInter render
        self.update_render_gameboard(self.gb)

    def check_game_state(self) -> None:
        """
        Call this method after a move has been made on the actual game board that is displayed by our Gui.

        This method should be called when a move is made on the actual game board, which is displayed by our Gui,
        rather than when the TreeAI is considering moves on copies of the game board.

        The methode checks if the game has a winner or has ended in a draw, or if it is still ongoing. The information
        will be conveyed to the user through various channels: the INFO log using logging.info(), STDOUT using print(),
        and if the game has ended, additionally a PopupWindow with the message will pop up.
        """

        if self.gb.winner > 0:
            if self.gb.winner == 3:
                msg = "The game ended in a draw (%s vs. %s) with a score of %d : %d!" % (
                    self.gb.player_ai[1],
                    self.gb.player_ai[2],
                    self.gb.win_counter[1],
                    self.gb.win_counter[2]
                )
                color_set = "draw"
            else:
                msg = "The game has ended. Player %d (%s) won with a score of %d : %d!" % (
                    self.gb.winner,
                    self.gb.player_ai[self.gb.winner],
                    self.gb.win_counter[1],
                    self.gb.win_counter[2]
                )
                if self.gb.winner == 1:
                    color_set = "player_1"
                else:
                    color_set = "player_2"

            # TODO error-popup
            # self.popup_windows_queue.push(
            #     PopupWindow(
            #         self.theme,
            #         self.screen,
            #         msg,
            #         font_size_message=17,
            #         callback_function=self.callback_popup_window_dismiss_button,
            #         color_set=color_set
            #     )
            # )
        else:
            msg = (
                    "Next up: Player %d (%s)! Score: %d : %d, %d moves made, %d moves remaining."
                    % (
                        self.gb.current_player,
                        self.gb.player_ai[self.gb.current_player],
                        self.gb.win_counter[1],
                        self.gb.win_counter[2],
                        self.gb.moves_made,
                        self.gb.remaining_moves
                    )
            )

        logging.info(msg)
        print(msg)

    def update_player_ai(self, player: int, player_ai: str = "Human") -> None:
        """
        Call this method, whenever the player_ai for one of both players changes.

        May be called from main.py when a new game is loaded from a saved game.
        """
        # Update Gameboard
        self.gb.player_ai[player] = player_ai

        # Tkinter specific
        self.player_ai[player].set(player_ai)

        # Write info log
        msg = "Player %d AI changed to: %s" % (player, player_ai)
        logging.info(msg)
        print(msg)

    def kill_tree_ai(self) -> None:
        pass

    def main_loop(self) -> None:
        """ The Tkinter main loop """
        self.master.mainloop()

    def menu_new_game(self):
        self.player_ai[1].set("Human")
        self.player_ai[2].set("Human")

        self.gb = GameBoard(self.gb_size_x, self.gb_size_y, self.verbose)

        self.canvas.delete("all")
        self.render_gameboard(self.gb)
        self.recent_filename = None

        self.player_messages.insert(tkinter.CURRENT, "Neues Spiel gestartet. Player 1 up.\nViel Erfolg!\n")
        self.next_player_color_field.itemconfigure(self.next_player_color_field_rectangle, fill=self.player_colors[
            self.gb.current_player])  # todo eigene "gui"-methode dafür machen die nur den player als param will

        logging.info("new game gui reset done")

    def menu_load_game(self):
        # TODO Use Savegames from kaese.savegames.savegames
        allowed_formats = [
            ('PKL-File', '*.pkl'),
            ('Any File', '*')
        ]
        file_name = tk_file_dialog.askopenfilename(parent=self.master, filetypes=allowed_formats,
                                                   title='Choose a .pkl file')
        if len(file_name) == 0:
            # TODO error-popup
            logging.error("game load error: no file selected")
            return

        file = open(file_name, "rb")
        if file is None:
            # TODO error-popup
            logging.error("game load error: read error")
            return

        gb_load = pickle.load(file)

        self.player_ai[1].set("Human")
        self.player_ai[2].set("Human")

        if gb_load.size_x != self.gb.size_x or gb_load.size_y != self.gb.size_y:
            # TODO besser eine neue funktion aufrufen die das ganze komplette fenster ganz neu macht
            logging.info("game load: resize to %dx%d" % (gb_load.size_x, gb_load.size_y))
            # self.line_distance = self.canvas_width / self.gb.size_x

        self.gb = gb_load
        logging.info("game loaded")
        self.recent_filename = file_name

        self.canvas.delete("all")
        self.render_gameboard(self.gb)

        self.player_messages.insert(tkinter.CURRENT,
                                    "Neues Spiel geladen. Player %d up.\nViel Erfolg!\n" % self.gb.current_player)
        self.next_player_color_field.itemconfigure(self.next_player_color_field_rectangle, fill=self.player_colors[
            self.gb.current_player])  # todo eigene "gui"-methode dafür machen die nur den player als param will

    def menu_save_game(self):
        # TODO Use Savegames from kaese.savegames.savegames
        if self.recent_filename is None:
            return self.menu_save_game_as()
        fh = open(self.recent_filename, "wb")
        pickle.dump(self.gb, fh)
        fh.close()
        logging.info("Game saved as %s" % self.recent_filename)

    def menu_save_game_as(self):
        # TODO Use Savegames from kaese.savegames.savegames
        allowed_formats = [
            ('PKL-File', '*.pkl'),
            ('Any File', '*')
        ]
        file_name = tk_file_dialog.asksaveasfilename(parent=self.master, filetypes=allowed_formats, title="Save as...")
        if len(file_name) == 0:
            # TODO error-popup
            logging.error("game save error: no filename selected")
            return

        # TODO file exists check und abfrage
        logging.info("Now saving under %s" % file_name)
        fh = open(file_name, "wb")
        pickle.dump(self.gb, fh)
        fh.close()

        self.recent_filename = file_name

    @staticmethod
    def menu_help():
        msg = '''\
Das grüne bzw. rote Quadrat ganz rechts unten im Fenster zeigt, wer grade am Zug ist.

Über die Menüs "Player 1" und "Player 2" kann man automatische Computer-Spieler aktivieren.

Zur Zeit kann man die Spielfeldgröße noch nur über die Datei kaese.py ändern.

Lies auch die Spielregeln!\
'''
        tk_message_box.showinfo("Help", msg)

    @staticmethod
    def menu_help_spielregeln():
        msg = '''\
Früher wurde auf einem Blatt Papier mit Rechen-Kästchen z.B. mit einem Kuli und einem Bleistift gespielt.

Dabei setzten beide Spieler abwechselnd einen Strich auf eine Kante der Kästchen.

Sobald ein Kästchen vollständig Umrandet ist, erobert der Spieler dieses Kästchen (z.B. "Kreuz" und "Kreis" für 
Spieler 1 und 2). Dabei spielt es keine Rolle von wem die anderen 3 Striche am Kästchen sind. (Im unserer 
Implementation werden dennoch die Striche in den Spieler-Farben angezeigt - das hat aber nur kosmetische Gründe.)

Der Außenrand vom Spielfeld zählt als bereits gezogener Strich; Hier sind also nur 3 bzw. 2 weitere Striche der 
Spieler nötig um das Kästchen vollständig zu umranden und in besitzt zu nehmen.

Wenn ein Spieler mit seinem Zug ein neues Feld erobert hat darf er erneut ziehen!\
'''
        tk_message_box.showinfo("Spielregeln", msg)

    @staticmethod
    def menu_about():
        msg = '''\
Käsekästchen

written in 2015, cleanup in 2021, 2023
by Guido Pannenbecker <info@sd-gp.de>

"THE BEER-WARE LICENSE" (Revision 42)\
'''
        tk_message_box.showinfo("About", msg)

    def menu_set_player1(self):
        self.update_player_ai(1, self.player_ai[1].get())
        logging.info("Player1 is now %s" % self.player_ai[1].get())

    def menu_set_player2(self):
        self.update_player_ai(2, self.player_ai[2].get())
        logging.info("Player2 is now %s" % self.player_ai[2].get())

    def check_ki(self):
        if self.gb.winner > 0:
            self.master.after(5000, self.check_ki)
            return

        try:
            player_ai = self.player_ai[self.gb.current_player].get()
            if player_ai == "StupidAI":
                ai = kaese.ai.stupid_ai.StupidAI()
                move = ai.get_next_move(self.gb, self.gb.current_player)
                self.gb.make_move(move)
                self.update_render_gameboard(self.gb)
            elif player_ai == "RandomAI":
                ai = kaese.ai.random_ai.RandomAI()
                move = ai.get_next_move(self.gb, self.gb.current_player)
                self.gb.make_move(move)
                self.update_render_gameboard(self.gb)
            elif player_ai == "SimpleAI":
                ai = kaese.ai.simple_ai.SimpleAI()
                move = ai.get_next_move(self.gb, self.gb.current_player)
                self.gb.make_move(move)
                self.update_render_gameboard(self.gb)
            elif player_ai == "NormalAI":
                ai = kaese.ai.normal_ai.NormalAI()
                move = ai.get_next_move(self.gb, self.gb.current_player)
                self.gb.make_move(move)
                self.update_render_gameboard(self.gb)
            elif player_ai == "BetterAI":
                ai = kaese.ai.better_ai.BetterAI()
                move = ai.get_next_move(self.gb, self.gb.current_player)
                self.gb.make_move(move)
                self.update_render_gameboard(self.gb)
            elif player_ai == "ClusterAI":
                ai = kaese.ai.cluster_ai.ClusterAI()
                move = ai.get_next_move(self.gb, self.gb.current_player)
                self.gb.make_move(move)
                self.update_render_gameboard(self.gb)
            elif player_ai == "TreeAI":
                ai = kaese.ai.tree_ai.TreeAI()
                move = ai.get_next_move(self.gb, self.gb.current_player, self.tree_ai_max_moves)
                self.gb.make_move(move)
                self.update_render_gameboard(self.gb)
            elif player_ai != "Human":
                self.player_messages.insert(tkinter.CURRENT, "%s is not yet supported!\n" % (
                    player_ai))
        # Catch any Exceptions raised by the AIs
        except Exception as err:
            # Disable AI, reset to Human player
            self.player_ai[self.gb.current_player].set("Human")

            # Write error message to logging and GUI
            msg = "Exception in %s: %s" % (player_ai, err)
            logging.error(msg, exc_info=True)
            self.player_messages.insert(tkinter.CURRENT, "%s\n" % msg)
            self.player_messages.insert(tkinter.CURRENT, "Reset Player %d to Human\n" % self.gb.current_player)

        delay = 2650
        if self.player_ai[1].get() == "Human" or self.player_ai[2].get() == "Human":
            delay = 1500
        self.master.after(delay, self.check_ki)  # todo delay konfigurierbar machen?

    def on_line_click(self, event):
        # logging.debug('Got object click', event.x, event.y, event.widget,)
        # logging.debug(event.widget.find_closest(event.x, event.y))
        if self.player_ai[self.gb.current_player].get() == "Human":
            line = event.widget.find_closest(event.x, event.y)[0]
            # self.canvas.itemconfigure(line, fill='white', activefill='white', width=5)
            move = self.line_widgets_to_move[line]
            move.player = self.gb.current_player
            move.player_ai = self.player_ai[self.gb.current_player].get()
            self.gb.make_move(move)
            self.update_render_gameboard(self.gb)

    def render_gameboard(self, gb):
        px = self.line_distance
        if px < 20:
            raise Exception(u"self.line_distance < 20, that is to small", px)
        # Zeichne Linien, verknüpfe onClick-Event, speichere Linien und passenden Zug in den beiden Dictionaries
        self.line_widgets_to_move = {}
        self.coords_to_line_widgets = {}
        for x in range(0, gb.size_x):
            for y in range(0, gb.size_y):
                if y < gb.size_y - 1:
                    line = self.canvas.create_line(x * px, (y + 1) * px, (x + 1) * px, (y + 1) * px, fill="#aaaaaa",
                                                   activefill="black", width=4, activewidth=8)
                    self.canvas.tag_bind(line, '<Button-1>', self.on_line_click)
                    self.line_widgets_to_move[line] = Move(x, y, 1)
                    self.coords_to_line_widgets[x, y, 1] = line
        for x in range(0, gb.size_x):
            for y in range(0, gb.size_y):
                if x < gb.size_x - 1:
                    line = self.canvas.create_line((x + 1) * px, y * px, (x + 1) * px, (y + 1) * px, fill="#aaaaaa",
                                                   activefill="black", width=4, activewidth=8)
                    self.canvas.tag_bind(line, '<Button-1>', self.on_line_click)
                    self.line_widgets_to_move[line] = Move(x, y, 0)
                    self.coords_to_line_widgets[x, y, 0] = line
        # Zeichne Aussenrand
        x = gb.size_x * px
        y = gb.size_y * px
        self.canvas.create_line(1, 1, x, 1, fill="blue", width=8)
        self.canvas.create_line(1, 1, 1, y, fill="blue", width=8)
        self.canvas.create_line(x, 1, x, y, fill="blue", width=8)
        self.canvas.create_line(1, y, x, y, fill="blue", width=8)

        self.update_render_gameboard(gb)

    def update_render_gameboard(self, gb):
        """call after a move was made"""
        px = self.line_distance
        for x in range(0, gb.size_x):
            for y in range(0, gb.size_y):
                k = gb.boxes[x][y]
                if k.owner > 0:
                    # todo jedes mal ein neues drüber legen??!?
                    self.canvas.create_rectangle((x * px) + 7, (y * px) + 7, ((x + 1) * px) - 7, ((y + 1) * px) - 7,
                                                 fill=self.player_colors[k.owner])
                if y < gb.size_y - 1:
                    if k.line_below > 0:
                        line = self.coords_to_line_widgets[x, y, 1]
                        self.canvas.itemconfigure(line, fill=self.player_colors[k.line_below],
                                                  activefill=self.player_colors[k.line_below], width=5)
                        # todo unbind tag?
                if x < gb.size_x - 1:
                    if k.line_right > 0:
                        line = self.coords_to_line_widgets[x, y, 0]
                        self.canvas.itemconfigure(line, fill=self.player_colors[k.line_right],
                                                  activefill=self.player_colors[k.line_right], width=5)
                        # todo unbind tag?
        if gb.winner > 0:
            if gb.winner == 3:
                # Draw
                self.player_messages.insert(tkinter.CURRENT, "Unentschieden!\nEndstand: %d zu %d\n" % (
                    gb.win_counter[1], gb.win_counter[2]))
                logging.info("Unentschieden! Endstand: %d zu %d" % (gb.win_counter[1], gb.win_counter[2]))
            else:
                self.player_messages.insert(tkinter.CURRENT, "Player %d (%s) hat gewonnen!\nEndstand: %d zu %d\n" % (
                    gb.winner, self.player_ai[gb.winner].get(), gb.win_counter[1], gb.win_counter[2]))
                logging.info("Player %d (%s) hat gewonnen! Endstand: %d zu %d" % (
                    gb.winner, self.player_ai[gb.winner].get(), gb.win_counter[1], gb.win_counter[2]))
        else:
            if gb.last_move is None:
                pass
            else:
                z = gb.last_move
                line = self.coords_to_line_widgets[z.x, z.y, z.horizontal]
                self.canvas.itemconfigure(line, fill=self.player_colors[z.player], activefill="blue", width=12)
            self.player_messages.insert(tkinter.CURRENT, "Player %d up.\n%d zu %d, noch %d Züge\n" % (
                gb.current_player, gb.win_counter[1], gb.win_counter[2], gb.remaining_moves))
            logging.info("Player %d up. %d zu %d, noch %d Züge" % (
                gb.current_player, gb.win_counter[1], gb.win_counter[2], gb.remaining_moves))
            self.next_player_color_field.itemconfigure(self.next_player_color_field_rectangle,
                                                       fill=self.player_colors[gb.current_player])
