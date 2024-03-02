"""
Various bits of helpful code, focusing on wrapping around curses,
  since curses is how we're getting user input from the terminal
  without sudo, and it appears to mess up display formatting if you
  also try to use print
"""

import curses
import os
import signal
import sys
import time
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location

from bot_control.BotInterface import BotInterface

_IS_INITIALISED = False
WEB_PRINT = False
PiBot: BotInterface


def cleanup():
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    PiBot.cleanup()


@dataclass
class CursesState:
    stdscr: curses.window
    current_line: int = 0
    max_lines: int = 0


def main_wrapper(main):
    def signal_handler(_, __):
        cleanup()
        exit(0)

    def wrap(local_stdscr):
        CursesState.stdscr = local_stdscr
        CursesState.max_lines = local_stdscr.getmaxyx()[0]  # Set max_lines
        signal.signal(signal.SIGINT, signal_handler)
        main()

    curses.wrapper(wrap)


def curse_print(text):
    CursesState.stdscr.addstr(CursesState.current_line, 0, text)
    CursesState.current_line += 1
    CursesState.stdscr.refresh()

    # Screen clearing logic
    if CursesState.current_line >= CursesState.max_lines:
        CursesState.stdscr.clear()
        CursesState.current_line = 0


def curse_getkey():
    try:
        return CursesState.stdscr.getkey()
    except:
        cleanup()
        exit(0)


def curse_noecho():
    curses.noecho()


class ControlProcedure:
    def __init__(self, control_loop_fn):
        self.control_loop_fn = control_loop_fn
        curse_noecho()

    def start_procedure(self):
        while True:
            inp = curse_getkey()
            self.control_loop_fn(inp)
            time.sleep(0.1)


def init_system():
    global _IS_INITIALISED, WEB_PRINT
    if _IS_INITIALISED:
        return

    is_rpi = None
    piBotModule = None

    # conditionally import a raspberry pi module
    bot_module_name = ""
    rpi_uname = "raspberrypi"
    is_rpi = os.uname().nodename == rpi_uname
    bot_module_name = "Bot" if is_rpi else "TestBot"

    spec = spec_from_file_location(
        f"bot_control.{bot_module_name}", f"./bot_control/{bot_module_name}.py"
    )

    try:
        piBotModule = module_from_spec(spec)
    except ImportError:
        print("Was unable to import a PiBot")
        exit(-1)

    sys.modules[f"bot_control.{bot_module_name}"] = piBotModule
    spec.loader.exec_module(piBotModule)

    global PiBot
    if is_rpi:
        PiBot = piBotModule.Bot
    else:
        PiBot = piBotModule.TestBot

    # check for verbosity level
    web_print = None
    for arg in sys.argv:
        if arg == "WEB_PRINT=1":
            web_print = 1
            break
        elif arg == "WEB_PRINT=0":
            web_print = 0
            break

    WEB_PRINT = (is_rpi and web_print == None) or web_print == 1
    _IS_INITIALISED = True


# initialise the system
init_system()
