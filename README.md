"Käsekästchen" is a game for 2 players, AIs are available.

# Description

"Käsekästchen" is a small programming exercise.

It implements the well-known game of the same name from school days.

You can play against the computer or a second player on the same computer.
Alternatively, you can also let two AIs play against each other.


## Get started
### How to install the game

Just clone form git:

`git clone git@gitlab.datenfalke.de:blinkenplus/kaese.git`

### Requirements

Python >= 3.6 is required.

Run `make install` or `pip install -r requirements.txt` or `python3 -m pip install -r requirements.txt`

### HowTo run the Game

Run:

`$ python3 main.py` or `make run`

### HowTo run the Tests

`make test` will run:

    coverage run -m unittest discover
    coverage report

#### Generate the coverage report

Use `make coverage` to run all tests and create an HTML report about the code coverage.


## Game Rules

In the past, the game was played on a sheet of paper with grid boxes, using a pen and a pencil, for example.

Both players take turns drawing a line on an edge of the boxes.

Once a box is completely surrounded by lines, the player who completes it captures that box (e.g., "X" for player 1 and "O" for player 2). It doesn't matter who drew the other 3 lines around the box.

In our implementation, the lines are still displayed in the respective player's colors, but it's purely cosmetic.

The outer edge of the playing field counts as an already drawn line. Therefore, only 3 or 2 additional lines are needed by the players to completely surround and capture the box.

If a player captures a new box with their move, they get to make another move!


## Technical Implementation of the Game Rules

From a technical perspective, we store the current owner (0 for no one, 1 and 2 for Player 1 and 2) for each box and whether the line to the right of the box and the line below the box are already occupied, and if so, by whom (0 for no one, 1 and 2 for Player 1 and 2) in a grid of `Box` objects.

The GameBoard class implements all the game rules and represents the current game state.

The GameBoard stores things like who is currently playing (`current_player`) and how the game board looks at the moment (`boxes[x][y]` contains `Box` objects that store the values for `owner`, `line_right`, and `line_below`).

GameBoard provides the methods `make_move(Move m)` and `is_valid_move(Move m)`.

Correspondingly, the `Move` object includes the x and y coordinates, an indication of whether we are referring to the right (vertical) or the bottom (horizontal) line, and which player (1 or 2) is making the move.


## Planned Features

  * Make the delay for AI players adjustable in game using the GUI.
  * Add more tests.
  * Implement network play functionality.
  * Allow customizable starting positions.
  * Add `make clean` and `make release` to Makefile.


## Known Bugs

  * Loading game states with a different game board size than the current one can lead to display errors in the TKInter GUI.


## Contribution

Your contributions to this project are highly appreciated! This project exists as a programming exercise, and your help in various areas is more than welcome. Whether you're interested in bug fixes, implementing new features, adding more unit tests, or performing code cleanup, your contributions are valuable and encouraged.

To contribute, you can either contact me directly via email at <info@sd-gp.de> or submit a pull request on GitLab. Your contributions will be reviewed and considered for merging into the project.


## Authors

* Guido Pannenbecker <info@sd-gp.de>


## Acknowledgments:

 * TobiX: In 2015, TobiX provided valuable assistance in addressing compatibility issues with Python 3.
 * Thomas Radek: In 2023, Thomas helped me with a lot of the logic in the code.

Thank you to everyone who has contributed to this project in any way. Your support and involvement are greatly appreciated.
