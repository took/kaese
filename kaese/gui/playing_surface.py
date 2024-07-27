from typing import Dict, Any, Union

import pygame
import logging

from kaese.gameboard.invalid_move_exception import InvalidMoveException
from kaese.gameboard.move import Move
from kaese.gui.abstract_gui import AbstractGui
from kaese.gui.themes.theme import Theme


class PlayingSurface:
    """The class implements the interactive visuals that display the current gameboard."""

    theme: Theme
    gui: AbstractGui
    verbose: Union[bool, int]

    gameboard_pos_x: int
    gameboard_pos_y: int
    coords_to_line_widgets: Dict[Any, pygame.Rect]

    def __init__(self, gui: AbstractGui, theme: Theme, verbose: Union[bool, int] = False) -> None:
        self.gui = gui
        self.theme = theme
        self.verbose = verbose

        self.gameboard_pos_x = 0
        self.gameboard_pos_y = 0
        self.coords_to_line_widgets = {}

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events for playing surface"""

        redraw = False
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_x, mouse_y = event.pos

            # Adjust mouse coordinates based on the offset of the gameboard
            adjusted_mouse_x = mouse_x - self.gameboard_pos_x
            adjusted_mouse_y = mouse_y - self.gameboard_pos_y

            if self.verbose > 1:
                logging.debug(
                    "Click event on Pixel x %d, y %d, adjusted for gameboard surface: x %d, y %d" %
                    (mouse_x, mouse_y, adjusted_mouse_x, adjusted_mouse_y)
                )

            for key, line in self.coords_to_line_widgets.items():
                x, y, horizontal = key
                if self.verbose > 2:
                    logging.debug(
                        "Click event: Check line x %d, y %d, horizontal %d "
                        "on Coords x %d, y %d, width %d, height %d" %
                        (x, y, horizontal, line.x, line.y, line.width, line.height)
                    )
                if line.collidepoint(adjusted_mouse_x, adjusted_mouse_y):
                    logging.debug("Click event on Line x %d, y %d, horizontal %d" % (x, y, horizontal))
                    move = Move(x, y, horizontal, self.gui.gb.current_player, "Human")
                    is_valid_move = False
                    try:
                        is_valid_move = self.gui.gb.is_valid_move(move)
                    except InvalidMoveException as err:
                        # Intentionally ignore any Exception here
                        if self.verbose:
                            logging.debug("Intentionally ignored: Not a valid Move: %s" % err, exc_info=True)
                        pass
                    if is_valid_move:
                        self.gui.make_move(move)
                        redraw = True
                        break

        return redraw

    def draw_gameboard(self, is_resize=False) -> None:
        """Draw the gameboard"""

        # Reset coords_to_line_widgets dict
        self.coords_to_line_widgets = {}

        # Define base position, width and minimum box size and line width
        pos_x = 150
        pos_y = 135

        max_width = int(self.gui.screen_width - pos_x - 150)
        max_height = int(self.gui.screen_height - pos_y - 10)

        min_line_width = 2
        min_box_size = 6

        boxes_count_x = self.gui.gb.size_x
        boxes_count_y = self.gui.gb.size_y

        # Calculate line width and box size

        # Box size should be 9 times the line width, where there is one line more than boxes.
        # This results in 10 "segments" per box plus one for the left most outer line.

        segments_count_x = (boxes_count_x * 10) + 1
        segments_count_y = (boxes_count_y * 10) + 1

        line_width = max(
            min_line_width,
            min(
                max_width // segments_count_x,
                max_height // segments_count_y
            )
        )

        boxes_space_x = max_width - (line_width * (boxes_count_x + 1))
        boxes_space_y = max_height - (line_width * (boxes_count_y + 1))
        boxes_space = min(boxes_space_x, boxes_space_y)
        box_size = boxes_space // max(boxes_count_x, boxes_count_y)
        box_size = max(min_box_size, box_size)

        # Calculate final width and height
        # TODO Make pos_x+surface_width globally available to position elements relative to gameboard
        # Also vielleicht ein paar Zeilen weiter unten in self.gameboard_pos_x2 oder self.gameboard_x_plus_width
        #  oder so bekannt machen?
        surface_width = line_width + ((box_size + line_width) * boxes_count_x)
        surface_height = line_width + ((box_size + line_width) * boxes_count_y)

        if is_resize and self.verbose:
            logging.debug(
                "resize verbose: surface_width %d, surface_height %d, box_size %d, line_width %d" %
                (surface_width, surface_height, box_size, line_width)
            )

        # Make pos_x und pos_y globally available to be able to calculate offset for click events
        self.gameboard_pos_x = pos_x
        self.gameboard_pos_y = pos_y

        # Create surface to draw on
        surface = pygame.Surface((surface_width, surface_height))
        surface.fill(self.theme.playing_surface_background_color)

        # Draw boxes in player colours
        for x in range(0, boxes_count_x):
            for y in range(0, boxes_count_y):
                owner = self.gui.gb.boxes[x][y].owner
                if owner == 1:
                    square_color = self.theme.gui_player_1_color
                elif owner == 2:
                    square_color = self.theme.gui_player_2_color
                else:
                    square_color = self.theme.playing_surface_box_background_color
                bx = (x * (box_size + line_width)) + line_width
                by = (y * (box_size + line_width)) + line_width
                pygame.draw.rect(surface, square_color, (bx, by, box_size, box_size))

        # Draw the lines to click on
        for x in range(0, boxes_count_x):
            for y in range(0, boxes_count_y):
                if x < boxes_count_x - 1:
                    # Draw line to the right of the box
                    player_1_color = self.theme.playing_surface_line_player_1_color
                    player_2_color = self.theme.playing_surface_line_player_2_color
                    if self.gui.gb.last_move and self.gui.gb.last_move.x == x and self.gui.gb.last_move.y == y \
                            and self.gui.gb.last_move.horizontal == 0:
                        player_1_color = self.theme.playing_surface_line_player_1_last_move_color
                        player_2_color = self.theme.playing_surface_line_player_2_last_move_color
                    owner = self.gui.gb.boxes[x][y].line_right
                    if owner == 1:
                        line_color = player_1_color
                    elif owner == 2:
                        line_color = player_2_color
                    else:
                        line_color = self.theme.playing_surface_line_default_color
                    lx = (line_width + box_size) * (x + 1)
                    ly = line_width + ((line_width + box_size) * y)
                    line = pygame.draw.rect(surface, line_color,
                                            (lx, ly, line_width, box_size))
                    self.coords_to_line_widgets[x, y, 0] = line

                if y < boxes_count_y - 1:
                    # Draw line below box
                    player_1_color = self.theme.playing_surface_line_player_1_color
                    player_2_color = self.theme.playing_surface_line_player_2_color
                    if self.gui.gb.last_move and self.gui.gb.last_move.x == x and self.gui.gb.last_move.y == y \
                            and self.gui.gb.last_move.horizontal == 1:
                        player_1_color = self.theme.playing_surface_line_player_1_last_move_color
                        player_2_color = self.theme.playing_surface_line_player_2_last_move_color
                    owner = self.gui.gb.boxes[x][y].line_below
                    if owner == 1:
                        line_color = player_1_color
                    elif owner == 2:
                        line_color = player_2_color
                    else:
                        line_color = self.theme.playing_surface_line_default_color
                    lx = line_width + ((line_width + box_size) * x)
                    ly = (line_width + box_size) * (y + 1)
                    line = pygame.draw.rect(surface, line_color,
                                            (lx, ly, box_size, line_width))
                    self.coords_to_line_widgets[x, y, 1] = line

        # Draw outer frame (top, bottom, left, right)
        pygame.draw.rect(surface, self.theme.playing_surface_border_color,
                         (0, 0, line_width, surface_height))
        pygame.draw.rect(surface, self.theme.playing_surface_border_color,
                         ((surface_width - line_width), 0, line_width, surface_height))
        pygame.draw.rect(surface, self.theme.playing_surface_border_color,
                         (0, 0, surface_width, line_width))
        pygame.draw.rect(surface, self.theme.playing_surface_border_color,
                         (0, (surface_height - line_width), surface_width, line_width))

        self.gui.screen.blit(surface, (pos_x, pos_y))
