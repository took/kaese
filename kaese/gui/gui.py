from datetime import datetime
from typing import List, Optional, Any, Union

import pygame
import logging
import threading

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
from kaese.gui.button import Button
from kaese.gui.gui_exception import GuiException
from kaese.gui.new_game_popup_window import NewGamePopupWindow
from kaese.gui.playing_surface import PlayingSurface
from kaese.gui.popup_window import PopupWindow
from kaese.gui.popup_windows_queue import PopupWindowsQueue
from kaese.gui.radio_button_list import RadioButtonList
from kaese.gui.text_box import TextBox
from kaese.gui.themes.theme import Theme
from kaese.savegames.savegames import Savegames


class Gui(AbstractGui):
    """
    Gui implements AbstractGui.
    """

    theme: Theme
    ai_interval: int
    player1: str
    player2: str
    verbose: Union[bool, int]

    available_ais: List[str]
    gb: GameBoard

    running: bool
    ai_timer: int

    ai_thread: Optional[threading.Thread]
    ai_thread_start_time: Any  # Is this int? Or something like pygame.milliseconds?
    running_tree_ai: Optional[kaese.ai.tree_ai.TreeAI]
    tree_ai_move: Optional[Move]
    tree_ai_max_moves: int

    screen_width: int
    screen_height: int

    screen: pygame.surface
    pygame_clock: pygame.time.Clock

    popup_windows_queue: PopupWindowsQueue

    new_game_button: Button
    load_button: Button
    save_button: Button
    backward_button: Button
    forward_button: Button
    truncate_history_button: Button
    player1_selector: RadioButtonList
    player2_selector: RadioButtonList

    playing_surface: PlayingSurface

    # Enable available AIs
    available_ais = [
        "Human",
        "RandomAI",
        "StupidAI",
        "SimpleAI",
        "NormalAI",
        "BetterAI",
        "ClusterAI",
        "TreeAI"
    ]

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
        self.gb = GameBoard(gb_size_x, gb_size_y, self.verbose)
        self.gb.player_ai = {
            1: player1,
            2: player2
        }

        # Init running state
        self.running = False
        self.ai_timer = 0

        self.ai_thread = None
        self.ai_thread_start_time = None
        self.running_tree_ai = None
        self.tree_ai_move = None

        # Init pygame
        pygame.init()

        self.screen_width = 800
        self.screen_height = 600
        pygame.display.set_caption("Käsekästchen")
        program_icon = pygame.image.load(
            "kaese/assets/icon-dark.png" if self.theme.get_name() == "Dark" else "kaese/assets/icon.png"
        )
        pygame.display.set_icon(program_icon)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)

        pygame.font.init()

        self.pygame_clock = pygame.time.Clock()
        self.popup_windows_queue = PopupWindowsQueue()

        self.init_buttons()
        self.playing_surface = PlayingSurface(self, self.theme, self.verbose)
        self.draw_all()

        msg = ("GUI initialized, Next Up: Player %d (%s)"
               % (self.gb.current_player, self.gb.player_ai[self.gb.current_player]))
        logging.debug(msg)

    def main_loop(self) -> None:
        """The main loop"""

        self.running = True
        while self.running:
            if self.handle_events():
                self.draw_all()
            self.pygame_clock.tick(60)

        pygame.quit()

    def handle_events(self) -> bool:
        """
        Handle pygame events

        Returns:
            bool: True if a redraw is needed, False otherwise.
        """

        redraw = False
        is_resize = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Handle QUIT event
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize event, enforce minimal size of 620x500px
                self.screen_width, self.screen_height = self.screen.get_size()
                if self.screen_width < 620 or self.screen_height < 500:
                    self.screen_width = 640  # max(500, self.screen_width)
                    self.screen_height = 520  # max(520, self.screen_height)
                    self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
                redraw = True
                is_resize = True
            elif event.type == pygame.VIDEOEXPOSE:
                # Handle window minimising/maximising
                self.screen_width = self.screen.get_width()
                self.screen_height = self.screen.get_height()
                redraw = True
                is_resize = True
            w = self.popup_windows_queue.get_front()
            if w:
                if w.handle_event(event):
                    redraw = True
            else:
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.playing_surface.handle_event(event):
                        redraw = True
                if self.new_game_button.handle_event(event):
                    redraw = True
                if self.load_button.handle_event(event):
                    redraw = True
                if self.save_button.handle_event(event):
                    redraw = True
                if self.backward_button.handle_event(event):
                    redraw = True
                if self.forward_button.handle_event(event):
                    redraw = True
                if self.truncate_history_button.handle_event(event):
                    redraw = True
                if self.player1_selector.handle_event(event):
                    redraw = True
                if self.player2_selector.handle_event(event):
                    redraw = True

        # Update the timer
        current_time = pygame.time.get_ticks()
        if current_time - self.ai_timer >= self.ai_interval:
            self.check_ai()
            self.ai_timer = current_time
            redraw = True

        if is_resize:
            logging.debug(
                "resize: screen_width %d, screen_height %d" %
                (self.screen.get_width(), self.screen.get_height())
            )

        return redraw

    def draw_all(self) -> None:
        """Draw all elements on main window"""

        # Clear the screen
        self.screen.fill(self.theme.gui_background_color)

        # Draw all elements
        self.playing_surface.draw_gameboard()
        self.draw_buttons()
        self.draw_next_player_and_score_indicator()
        w = self.popup_windows_queue.get_front()
        if w:
            w.draw()

        # Update the screen
        pygame.display.flip()

    def init_buttons(self) -> None:
        """Init the New, Load and Save buttons and RadioButtons for each Player"""

        initial_selected_option_player1 = self.player1
        initial_selected_option_player2 = self.player2

        # Position of buttons
        pos_x = 10
        pos_y = 10

        width_std_buttons = 80
        height = 35

        font_size = 27
        font_size_radio_buttons = 17
        font_name = self.theme.gui_font_name

        distance = 8

        self.new_game_button = Button(
            self.theme,
            self.screen,
            pos_x,
            pos_y,
            width_std_buttons,
            height,
            "New",
            font_size,
            font_name,
            self.callback_new_game_button
        )

        self.load_button = Button(
            self.theme,
            self.screen,
            pos_x + width_std_buttons + distance,
            pos_y,
            width_std_buttons,
            height,
            "Load",
            font_size,
            font_name,
            self.callback_load_button
        )

        self.save_button = Button(
            self.theme,
            self.screen,
            pos_x + (2 * (width_std_buttons + distance)),
            pos_y,
            width_std_buttons,
            height,
            "Save",
            font_size,
            font_name,
            self.callback_save_button
        )

        width_history_buttons = 50
        self.backward_button = Button(
            self.theme,
            self.screen,
            0,  # Will be set in draw_buttons()
            pos_y,
            width_history_buttons,
            height,
            "<-",
            font_size,
            font_name,
            self.callback_backward_button,
            True
        )
        self.forward_button = Button(
            self.theme,
            self.screen,
            0,  # Will be set in draw_buttons()
            pos_y,
            width_history_buttons,
            height,
            "->",
            font_size,
            font_name,
            self.callback_forward_button,
            True
        )
        self.truncate_history_button = Button(
            self.theme,
            self.screen,
            0,  # Will be set in draw_buttons()
            pos_y,
            width_std_buttons,
            height,
            "Truncate",
            font_size // 2,
            font_name,
            self.callback_truncate_history_button,
            True
        )

        radius_radio_buttons = 9
        width_radio_button_list = 140
        self.player1_selector = RadioButtonList(
            self.theme,
            self.screen,
            pos_x,
            135,
            width_radio_button_list,
            height,
            distance,
            radius_radio_buttons,
            (255, 0, 0),
            initial_selected_option_player1,
            self.available_ais,
            font_size_radio_buttons,
            font_name,
            self.callback_player1_radio_buttons
        )

        self.player2_selector = RadioButtonList(
            self.theme,
            self.screen,
            int(self.screen_width - width_radio_button_list),
            135,
            width_radio_button_list,
            height,
            distance,
            radius_radio_buttons,
            (0, 255, 0),
            initial_selected_option_player2,
            self.available_ais,
            font_size_radio_buttons,
            font_name,
            self.callback_player2_radio_buttons
        )

    def draw_buttons(self) -> None:
        """Draw the New, Load and Save buttons and RadioButtons for each Player"""
        # Draw New Game Button
        self.new_game_button.draw()

        # Draw Load Game Button
        self.load_button.draw()

        # Draw Save Game Button
        self.save_button.draw()

        # Draw History Back Button
        history_buttons_distance = 6
        history_buttons_offset = (
                self.backward_button.rect.width
                + self.forward_button.rect.width
                + self.truncate_history_button.rect.width
                + 2 * history_buttons_distance
                + 15  # Align with next_player_and_score_indicator
        )
        self.backward_button.rect.x = int(self.screen_width - history_buttons_offset)
        if self.gb.move_history_pointer == 0:
            self.backward_button.render_button_inactive = True
        else:
            self.backward_button.render_button_inactive = False
        self.backward_button.draw()

        # Draw History Forward Button
        self.forward_button.rect.x = int(
            self.screen_width
            - history_buttons_offset
            + self.backward_button.rect.width
            + history_buttons_distance
        )
        if self.gb.move_history_pointer >= len(self.gb.move_history):
            self.forward_button.render_button_inactive = True
        else:
            self.forward_button.render_button_inactive = False
        self.forward_button.draw()

        # Draw Truncate History Button
        self.truncate_history_button.rect.x = int(
            self.screen_width
            - history_buttons_offset
            + self.backward_button.rect.width
            + self.forward_button.rect.width
            + 2 * history_buttons_distance
        )
        if self.gb.move_history_pointer >= len(self.gb.move_history):
            self.truncate_history_button.render_button_inactive = True
        else:
            self.truncate_history_button.render_button_inactive = False
        self.truncate_history_button.draw()

        # Draw RadioButtonList to select AI for Player 1
        self.player1_selector.draw()

        # Draw RadioButtonList to select AI for Player 2
        self.player2_selector.x = int(self.screen_width - self.player2_selector.width)
        self.player2_selector.draw()

    def draw_next_player_and_score_indicator(self) -> None:
        """Draw the indicator that shows, which player is up next and the current game score"""
        # Color for player that is up next
        if self.gb.current_player == 1:
            player_color = self.theme.gui_player_1_color  # Red for player 1
        else:
            player_color = self.theme.gui_player_2_color  # Green for player 2

        # Setup Font
        font_name = self.theme.gui_font_name
        font_color = self.theme.gui_font_color
        big_font_size = 36
        medium_font_size = 28
        smaller_font_size = 16

        # Be sure, pygame.font.init() has already been called in your project before!
        big_font_obj = pygame.font.SysFont(font_name, big_font_size)
        medium_font_obj = pygame.font.SysFont(font_name, medium_font_size)

        # Setup shared Positions and Dimensions
        text_row_1_y = 50
        pos_row_2_y = 90
        box_height = 30
        border_width = 3

        # Draw Next Up Box
        text_next_up_x = 42
        pos_next_up_box_x = 15
        box_next_up_width = 180

        text_next_up_surface = big_font_obj.render("Next up", True, font_color)
        self.screen.blit(text_next_up_surface, (text_next_up_x, text_row_1_y))

        TextBox(
            self.theme,
            self.screen,
            pos_next_up_box_x, pos_row_2_y, box_next_up_width, box_height,
            border_width,
            text_left="Player %d" % self.gb.current_player,
            text_right=self.gb.player_ai[self.gb.current_player],
            font_size=smaller_font_size,
            font_color=player_color
        ).draw()

        if self.ai_thread and self.running_tree_ai and self.running_tree_ai.cnt_move_nr:
            TextBox(
                self.theme,
                self.screen,
                pos_next_up_box_x + box_next_up_width + 10, pos_row_2_y + 2, box_next_up_width, box_height - 4,
                1,
                text_left="...",
                text_right="Test move %d/%d"
                           % (self.running_tree_ai.cnt_move_nr, self.running_tree_ai.cnt_valid_moves),
                font_size=smaller_font_size,
                font_color=player_color
            ).draw()

        # Draw Points Boxes
        point_x_offset = 65
        box_points_width = 50
        text_score_x = int(self.screen_width - point_x_offset - 54)
        pos_points1_box_x = int(self.screen_width - point_x_offset - 65)
        pos_points2_box_x = int(self.screen_width - point_x_offset)
        pos_colon_x = int(self.screen_width - point_x_offset - 11)

        text_score_surface = big_font_obj.render("Score", True, font_color)
        self.screen.blit(text_score_surface, (text_score_x, text_row_1_y))
        text_colon_surface = medium_font_obj.render(":", True, font_color)
        self.screen.blit(text_colon_surface, (pos_colon_x, pos_row_2_y))

        TextBox(
            self.theme,
            self.screen,
            pos_points1_box_x, pos_row_2_y, box_points_width, box_height,
            border_width,
            text_right="%d" % self.gb.win_counter[1],
            font_size=smaller_font_size,
            font_color=self.theme.gui_player_1_color
        ).draw()

        TextBox(
            self.theme,
            self.screen,
            pos_points2_box_x, pos_row_2_y, box_points_width, box_height,
            border_width,
            text_left="%d" % self.gb.win_counter[2],
            font_size=smaller_font_size,
            font_color=self.theme.gui_player_2_color
        ).draw()

    def update_player_ai(self, player: int, player_ai: str = "Human") -> None:
        """
        Call this method, whenever the player_ai for one of both players changes.

        Examples are callback_player1_radio_buttons() and 2, and exceptions in check_ai().
        """
        self.gb.player_ai[player] = player_ai

        self.player1_selector.selected_option = self.gb.player_ai[1]
        for i, button in enumerate(self.player1_selector.buttons):
            if self.player1_selector.selected_option == button.text:
                button.is_selected = True
            else:
                button.is_selected = False

        self.player2_selector.selected_option = self.gb.player_ai[2]
        for i, button in enumerate(self.player2_selector.buttons):
            if self.player2_selector.selected_option == button.text:
                button.is_selected = True
            else:
                button.is_selected = False

        msg = "Player %d AI changed to: %s" % (player, player_ai)
        logging.info(msg)
        print(msg)

    def make_move(self, move: Move) -> None:
        """Make move on gb and redraw gameboard"""
        if self.gb.move_history_pointer != len(self.gb.move_history):
            # Deny move
            return
        self.gb.make_move(move)
        self.gb.last_move = Move(move.x, move.y, move.horizontal, move.player, move.player_ai)
        self.check_game_state()

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

            self.popup_windows_queue.push(
                PopupWindow(
                    self.theme,
                    self.screen,
                    msg,
                    font_size_message=17,
                    callback_function=self.callback_popup_window_dismiss_button,
                    color_set=color_set
                )
            )
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

    def check_ai(self) -> None:
        """Run AI if current player is AI"""

        # Skip if game has already ended
        if self.gb.winner > 0:
            return

        # Pause AI if there is a PopupWindow
        if not self.popup_windows_queue.is_empty():
            return

        # Pause AI if move_history_pointer does not point to the last move in the game
        if self.gb.move_history_pointer < len(self.gb.move_history):
            return

        if self.verbose > 1:
            logging.debug("Check AI every %d milliseconds" % self.ai_interval)

        # Check settings and run according AI
        current_time = pygame.time.get_ticks()
        current_player = self.gb.current_player
        player_ai = self.gb.player_ai[current_player]
        try:
            if player_ai == "StupidAI":
                ai = kaese.ai.stupid_ai.StupidAI(self.verbose)
                move = ai.get_next_move(self.gb, current_player)
                self.make_move(move)
            elif player_ai == "RandomAI":
                ai = kaese.ai.random_ai.RandomAI(self.verbose)
                move = ai.get_next_move(self.gb, current_player)
                self.make_move(move)
            elif player_ai == "SimpleAI":
                ai = kaese.ai.simple_ai.SimpleAI(self.verbose)
                move = ai.get_next_move(self.gb, current_player)
                self.make_move(move)
            elif player_ai == "NormalAI":
                ai = kaese.ai.normal_ai.NormalAI(self.verbose)
                move = ai.get_next_move(self.gb, current_player)
                self.make_move(move)
            elif player_ai == "BetterAI":
                ai = kaese.ai.better_ai.BetterAI(self.verbose)
                move = ai.get_next_move(self.gb, current_player)
                self.make_move(move)
            elif player_ai == "ClusterAI":
                ai = kaese.ai.cluster_ai.ClusterAI(self.verbose)
                move = ai.get_next_move(self.gb, current_player)
                self.make_move(move)
            elif player_ai == "TreeAI":
                if self.ai_thread:
                    if not self.running_tree_ai.killed:
                        if self.ai_thread.is_alive():
                            if self.verbose is int and self.verbose > 1:  # At least "very verbose"
                                logging.debug(
                                    "--TreeAI thread Player %d--  Waiting for TreeAI thread since %d seconds..."
                                    % (current_player, int((current_time - self.ai_thread_start_time) / 1000))
                                )
                        else:
                            msg = "--TreeAI thread Player %d--  TreeAI thread finished after %d seconds!" % (
                                current_player,
                                int((current_time - self.ai_thread_start_time) / 1000)
                            )
                            logging.info(msg)
                            print(msg)

                            self.ai_thread.join()
                            move = self.tree_ai_move
                            self.ai_thread = None
                            if move:
                                self.make_move(move)
                else:
                    msg = "--TreeAI thread Player %d--  Starting new TreeAI thread..." % current_player
                    logging.info(msg)
                    print(msg)
                    self.ai_thread = threading.Thread(target=self.run_tree_ai)
                    self.ai_thread_start_time = current_time
                    self.ai_thread.start()
            elif player_ai != "Human":
                msg = "Error: AI '%s' is not yet supported!" % player_ai
                raise GuiException(msg)

        # Catch any Exceptions raised by the AIs
        except Exception as err:
            # Write error message using logging, STDOUT and PopUp window
            msg = "Exception in %s, reset Player %d to 'Human': %s" % (player_ai, current_player, err)
            logging.error(msg, exc_info=True)
            print("Error, see logfile for details: %s" % msg)
            self.popup_windows_queue.push(
                PopupWindow(
                    self.theme,
                    self.screen,
                    "An error occurred, see logfile for details!",
                    font_size_message=14,
                    callback_function=self.callback_popup_window_dismiss_button
                )
            )

            # Disable AI, reset to Human player
            self.update_player_ai(current_player, "Human")

    def run_tree_ai(self) -> None:
        self.running_tree_ai = kaese.ai.tree_ai.TreeAI(self.verbose, self.tree_ai_max_moves)
        try:
            move = self.running_tree_ai.get_next_move(self.gb, self.gb.current_player)
            if not self.running_tree_ai.killed:
                self.tree_ai_move = move
        except Exception as err:
            # Write error message using logging, STDOUT and PopUp window
            msg = "Exception in %s: %s" % (self.running_tree_ai.__class__.__name__, err)
            logging.error(msg, exc_info=True)
            print("Error, see logfile for details: %s" % msg)
            self.popup_windows_queue.push(
                PopupWindow(
                    self.theme,
                    self.screen,
                    "An error occurred, see logfile for details!",
                    font_size_message=14,
                    callback_function=self.callback_popup_window_dismiss_button
                )
            )

    def kill_tree_ai(self) -> None:
        if self.running_tree_ai:
            self.running_tree_ai.killed = True
        self.ai_thread = None

    def callback_popup_window_dismiss_button(self) -> None:
        """Called, when Dismiss button in a popup window was clicked"""
        if not self.popup_windows_queue.is_empty():
            self.popup_windows_queue.pop()

    def callback_popup_window_new_game_button(self) -> None:
        """Called, when OK button in "New Game" popup window was clicked"""
        if not self.popup_windows_queue.is_empty():
            w = self.popup_windows_queue.get_front()
            gb_size_x = w.gameboard_x
            gb_size_y = w.gameboard_y

            msg = "New Game! Size %d x %d" % (gb_size_x, gb_size_y)
            logging.info(msg)
            print(msg)

            self.gb = GameBoard(gb_size_x, gb_size_y, self.verbose)

            self.gb.player_ai = {
                1: "Human",
                2: "Human"
            }
            self.player1_selector.selected_option = "Human"
            for i, button in enumerate(self.player1_selector.buttons):
                if self.player1_selector.selected_option == button.text:
                    button.is_selected = True
                else:
                    button.is_selected = False
            self.player1_selector.draw()
            self.player2_selector.selected_option = "Human"
            for i, button in enumerate(self.player2_selector.buttons):
                if self.player2_selector.selected_option == button.text:
                    button.is_selected = True
                else:
                    button.is_selected = False
            self.player2_selector.draw()

            self.gb.last_move = None
            self.kill_tree_ai()

            self.popup_windows_queue.pop()

    def callback_new_game_button(self) -> None:
        """Called, when New game button was clicked"""

        self.new_game_button.is_mouseover = False
        self.popup_windows_queue.push(
            NewGamePopupWindow(
                self.theme,
                self.screen,
                self.gb.size_x,
                self.gb.size_y,
                callback_function_cancel=self.callback_popup_window_dismiss_button,
                callback_function_ok=self.callback_popup_window_new_game_button,
            )
        )

    def callback_load_button(self) -> None:
        """Called, when Load button was clicked"""
        try:
            # TODO Provide list with filenames to choose from
            filename = 'latest.json'

            msg = "Load Game \"%s\"! Size %d x %d" % (filename, self.gb.size_x, self.gb.size_y)
            logging.info(msg)
            print(msg)

            self.kill_tree_ai()
            self.gb = Savegames.load_game(filename, reset_players_to_human=True, verbose=self.verbose)
            self.update_player_ai(1, self.gb.player_ai[1])
            self.update_player_ai(2, self.gb.player_ai[2])

            self.popup_windows_queue.push(
                PopupWindow(
                    self.theme,
                    self.screen,
                    msg,
                    font_size_message=12,
                    callback_function=self.callback_popup_window_dismiss_button
                )
            )
        except Exception as err:
            # Write error message using logging, STDOUT and PopUp window
            msg = "Exception in LoadGame: %s" % err
            logging.error(msg, exc_info=True)
            print("Error, see logfile for details: %s" % msg)
            self.popup_windows_queue.push(
                PopupWindow(
                    self.theme,
                    self.screen,
                    "An error occurred, see logfile for details!",
                    font_size_message=14,
                    callback_function=self.callback_popup_window_dismiss_button
                )
            )

    def callback_save_button(self) -> None:
        """Called, when Save button was clicked"""
        try:
            current_datetime = datetime.now()
            datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

            player1 = self.gb.player_ai[1]
            player2 = self.gb.player_ai[2]
            move_nr = self.gb.move_history_pointer
            size_x = self.gb.size_x
            size_y = self.gb.size_y
            moves_cnt = (size_x * (size_y - 1)) + ((size_x - 1) * size_y)
            history = ""
            diff = len(self.gb.move_history) - self.gb.move_history_pointer
            if diff > 0:
                history = "(+%d)" % diff

            # filename = "2023-08-11_12:28:23_Human_vs_BetterAI_Move_22(+12)_of_45_(4x7).json"
            filename = ("%s_%s_vs_%s_Move_%d%s_of_%d_(%dx%d).json" %
                        (datetime_str, player1, player2, move_nr, history, moves_cnt, size_x, size_y))

            msg = "Save game as \"%s\"" % filename
            logging.info(msg)
            print(msg)

            Savegames.save_game(self.gb, filename, overwrite=False)

            self.popup_windows_queue.push(
                PopupWindow(
                    self.theme,
                    self.screen,
                    msg,
                    font_size_message=12,
                    callback_function=self.callback_popup_window_dismiss_button
                )
            )
        except Exception as err:
            # Write error message using logging, STDOUT and PopUp window
            msg = "Exception in SaveGame: %s" % err
            logging.error(msg, exc_info=True)
            print("Error, see logfile for details: %s" % msg)
            self.popup_windows_queue.push(
                PopupWindow(
                    self.theme,
                    self.screen,
                    "An error occurred, see logfile for details!",
                    font_size_message=14,
                    callback_function=self.callback_popup_window_dismiss_button
                )
            )

    def callback_backward_button(self) -> None:
        """Called, when History-Back button was clicked"""
        self.forward_button.is_mouseover = False
        if 0 < self.gb.move_history_pointer <= len(self.gb.move_history):
            msg = "Backward one move in history"
            logging.info(msg)
            print(msg)
            self.kill_tree_ai()
            # Take back one move
            self.gb.take_back_one_move()

    def callback_forward_button(self) -> None:
        """Called, when History-Forward button was clicked"""
        if self.gb.move_history_pointer < len(self.gb.move_history):
            self.kill_tree_ai()
            move = self.gb.move_history[self.gb.move_history_pointer]
            try:
                msg = "Forward one move in history"
                logging.info(msg)
                print(msg)
                # Make the move again
                self.gb.make_move(move, skip_append_to_history=True, ignore_current_selected_player=True)
                self.gb.last_move = move
                self.check_game_state()
                self.gb.move_history_pointer += 1
            except Exception as err:
                # Write error message using logging, STDOUT and PopUp window
                msg = "Exception while repeating move for %s: %s" % (move.player_ai, err)
                logging.error(msg, exc_info=True)
                print("Error, see logfile for details: %s" % msg)
                self.popup_windows_queue.push(
                    PopupWindow(
                        self.theme,
                        self.screen,
                        "An error occurred, see logfile for details!",
                        font_size_message=14,
                        callback_function=self.callback_popup_window_dismiss_button
                    )
                )

    def callback_truncate_history_button(self) -> None:
        """Called, when Truncate-Back button was clicked"""
        if self.gb.move_history_pointer < len(self.gb.move_history):
            self.kill_tree_ai()
            msg = "Truncate history"
            logging.info(msg)
            print(msg)
            # Truncate history after current move
            self.gb.truncate_history()

    def callback_player1_radio_buttons(self) -> None:
        """Called, when RadioButton for Player 1 was clicked"""
        self.update_player_ai(1, self.player1_selector.selected_option)

    def callback_player2_radio_buttons(self) -> None:
        """Called, when RadioButton for Player 2 was clicked"""
        self.update_player_ai(2, self.player2_selector.selected_option)
