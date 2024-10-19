"""
This simply allows you to control the bot via power control
"""

from bot_control.PowerControl import PowerControlBot
from common import ControlProcedure, PiBot, curse_print, main_wrapper


def control_loop(posBot: PowerControlBot, letter: str):
    if letter == "w":
        curse_print("Moving forward")
        posBot.move_forward()
    elif letter == "a":
        curse_print("Turning left")
        posBot.turn_left()
    elif letter == "s":
        curse_print("Moving backward")
        posBot.move_backward()
    elif letter == "d":
        curse_print("Turning right")
        posBot.turn_right()
    elif letter == "x":
        curse_print("Stopping")
        posBot.stop()
    else:
        curse_print(f"Unknown command: {letter}")


def main():
    bot = PiBot()
    posControlBot = PowerControlBot(bot, 50)

    def control_loop_fn(inp: str):
        control_loop(posControlBot, inp)

    control_proc = ControlProcedure(control_loop_fn)
    control_proc.start_procedure()


if __name__ == "__main__":
    main_wrapper(main)
