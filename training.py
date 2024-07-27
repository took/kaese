import logging
import argparse
import os
import sys

from kaese.gui.gui import Gui
from kaese.gui.themes.themes_manager import ThemesManager
from kaese.savegames.savegames import Savegames

# TODO This import shall be conditional
from kaese.gui.tkinter_gui import TkinterGui


def type_theme(theme):
    available_themes = ThemesManager.get_available_themes()
    theme_lower = theme.lower()
    if theme_lower.replace("_", "") in map(str.lower, available_themes):
        # Capitalize the first letter of each word to convert "foo_bar" to "FooBar" (or "fnord" to "Fnord")
        theme_words = theme_lower.split('_')  # Split by underscores if present
        theme_formatted = ''.join(word.capitalize() for word in theme_words)
        if theme_formatted in available_themes:
            return theme_formatted
    raise argparse.ArgumentTypeError("'%s' is not a valid theme. Use %s" % (theme, [x for x in available_themes]))


def type_player_ai(player_ai):
    if player_ai is None:
        return None
    available_ais = Gui.available_ais
    if player_ai in available_ais:
        return player_ai
    raise argparse.ArgumentTypeError("'%s' is not a valid AI. Please use %s" % (player_ai, [x for x in available_ais]))


def type_loglevel(level):
    try:
        loglevel = getattr(logging, level.upper())
    except AttributeError:
        raise argparse.ArgumentTypeError(
            "'%s' is not a valid log level. Please use %s"
            % (level, [x for x in logging._nameToLevel.keys() if isinstance(x, str)])
        )
    return loglevel


def main():
    # Initialise ArgumentParser
    parser = argparse.ArgumentParser(description="Cheese Box Game")
    parser.add_argument("-tk", "--tkinter", action="store_true",
                        help="Use TkInter GUI instead of default PyGame (Default: False)")
    parser.add_argument("-t", "--theme", type=type_theme, default="Light",
                        help="Theme (Default: Light, Valid: Light, Dark, Original)")
    parser.add_argument("-x", "--size-x", type=int, default=None,
                        help="Width of the game board (Default: 5, Valid: 3-50)")
    parser.add_argument("-y", "--size-y", type=int, default=None,
                        help="Height of the game board (Default: 7, Valid: 3-50)")
    parser.add_argument("-f", "--file", type=str, default=None,
                        help="Filename of save-game in the ./savegames/ folder to load from (Default: None)")
    parser.add_argument("-s", "--save", type=str, default="latest.json",
                        help="Filename to save to on exit (Default: latest.json)")
    parser.add_argument("-i", "--ip", type=str, default=None,
                        help="IP to connect to (Default: None)")
    parser.add_argument("-p", "--port", type=int, default=2345,
                        help="Port to connect to (Default: 2345)")
    parser.add_argument("--ai-interval", type=int, default=1500,
                        help="Delay in milliseconds for AIs before they take their next turn (Default: 1500)")
    parser.add_argument("-p1", "--player1", type=type_player_ai, default=None,
                        help="AI for Player 1 (Default: Human, Recommended: Human, RandomAI, BetterAI or ClusterAI)")
    parser.add_argument("-p2", "--player2", type=type_player_ai, default=None,
                        help="AI for Player 2 (Default: Human, Recommended: Human, RandomAI, BetterAI or ClusterAI)")
    parser.add_argument("--logfile", default="app.log",
                        help="Path to the log file (Default: app.log)")
    parser.add_argument("-l", "--loglevel", type=type_loglevel, default="WARNING",
                        help="Log level verbosity (Default: WARNING, Recommended: DEBUG, INFO, WARNING or ERROR)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output (Default: False)")
    parser.add_argument("-vv", "--very-verbose", action="store_true",
                        help="Very verbose output (Default: False)")
    parser.add_argument("-vvv", "--very-very-verbose", action="store_true",
                        help="Very very verbose output (Default: False)")
    parser.add_argument("-m", "--moves", type=int, default=20,
                        help="Max moves for tree AI (Default: 20)")

    args = parser.parse_args()

    # Check for conflicts in arguments
    if args.file and (args.size_x or args.size_y):
        raise argparse.ArgumentError(None, "Arguments --size-x and --size-y are not allowed "
                                           "together with --file.")

    if args.ip and (args.file or args.tkinter):
        raise argparse.ArgumentError(None, "Arguments --file and --tkinter are not allowed "
                                           "together with --ip.")

    # Set defaults for arguments size_x and size_y
    if not args.size_x:
        args.size_x = 5
    if not args.size_y:
        args.size_y = 7

    # Configure the logging module
    pid = os.getpid()
    logging.basicConfig(
        filename=args.logfile,
        level=args.loglevel,
        datefmt="%Y-%m-%d %H:%M:%S",
        format=f"%(asctime)s %(name)s PID {pid} %(levelname)s - %(message)s"
    )

    # Set verbosity level
    verbose = False
    if args.very_very_verbose:
        verbose = 3
    elif args.very_verbose:
        verbose = 2
    elif args.verbose:
        verbose = 1

    if verbose:
        msg = "Application started with verbosity %d." % verbose
        logging.info(msg)
        if args.loglevel != logging.DEBUG:
            msg = "%s Use --loglevel DEBUG to see even more events in logfile \"%s\"!" % (msg, args.logfile)
        else:
            msg = "%s See even more events in logfile \"%s\"!" % (msg, args.logfile)
        print(msg)
    else:
        logging.info("Application started.")

    try:

        # Select Theme
        selected_theme = ThemesManager.get_theme(args.theme)

        # Configure and initialize GUI
        if args.tkinter:
            # TkInter
            gui = TkinterGui(
                theme=selected_theme,
                gb_size_x=min(50, max(3, args.size_x)),
                gb_size_y=min(50, max(3, args.size_y)),
                ai_interval=args.ai_interval,
                player1=args.player1 if args.player1 is not None else "Human",
                player2=args.player2 if args.player2 is not None else "Human",
                tree_ai_max_moves=args.moves,
                verbose=verbose
            )
        else:
            # Pygame (default)
            gui = Gui(
                theme=selected_theme,
                gb_size_x=min(50, max(3, args.size_x)),
                gb_size_y=min(50, max(3, args.size_y)),
                ai_interval=args.ai_interval,
                player1=args.player1 if args.player1 is not None else "Human",
                player2=args.player2 if args.player2 is not None else "Human",
                tree_ai_max_moves=args.moves,
                verbose=verbose
            )

        # Load save-game if requested
        if args.file:
            filename = args.file
            gui.gb = Savegames.load_game(filename, reset_players_to_human=False, verbose=gui.verbose)
            if args.player1 is not None:
                gui.update_player_ai(1, args.player1)
            else:
                gui.update_player_ai(1, gui.gb.player_ai[1])
            if args.player2 is not None:
                gui.update_player_ai(2, args.player2)
            else:
                gui.update_player_ai(2, gui.gb.player_ai[2])
            msg = "Load Game \"%s\"! Size %d x %d" % (filename, gui.gb.size_x, gui.gb.size_y)
            logging.info(msg)
            print(msg)

        # Run the main loop
        gui.main_loop()

        # Stop any running threads
        gui.kill_tree_ai()

        # Save save-game if requested
        if args.save:
            filename = args.save
            Savegames.save_game(gui.gb, filename, overwrite=True)
            msg = "Game saved as \"%s\"" % filename
            logging.info(msg)
            print(msg)

    except Exception as err:
        msg = "A critical error has occurred: %s" % err
        logging.critical(msg, exc_info=True)
        print(msg)
        raise err

    # Application termination and cleanup
    logging.info("Application terminated.")
    print("Application terminated. Goodbye!")
    sys.exit()


if __name__ == "__main__":
    main()
