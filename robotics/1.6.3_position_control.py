"""
This demonstrates the code for Practical 1, specifically via:
```
posBot.move_square(forward_dist=833, turn_amount=250)
```
This makes the robot move in a square using position control, callibrated by
  our empirically derived values
"""

import time

from bot_control.PositionControl import Bot, PositionControlBot
from common import curse_getkey, curse_print, main_wrapper


def move_square(posControlBot: PositionControlBot, forward_dist=833, turn_amount=256):
    for _ in range(4):
        posControlBot.move_forward(forward_dist)
        time.sleep(1.5)
        posControlBot.turn_left(turn_amount)
        time.sleep(1)


def control_loop(posBot: PositionControlBot, letter: str):
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
    elif letter == "y":
        curse_print("Moving in a square")
        move_square(posBot, forward_dist=833, turn_amount=250)
    elif letter == "x":
        curse_print("Stopping")
        posBot.stop()
    else:
        curse_print(f"Unknown command: {letter}")


def main():
    bot = Bot()
    posControlBot = PositionControlBot(bot, 300)

    while True:
        key = curse_getkey()
        control_loop(posControlBot, key)
        time.sleep(0.1)


if __name__ == "__main__":
    main_wrapper(main)
