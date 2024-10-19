"""
The robot utilises the touch sensors to avoid obstacles, if it is hit head on
  it'll move in a random direction
"""

import random
import time

from bot_control.BotInterface import BotInterface
from bot_control.PositionControl import PositionControlBot
from bot_control.VelocityControl import VelocityControlBot
from common import PiBot, curse_print, main_wrapper


def control_loop(
    bot: BotInterface, posBot: PositionControlBot, velBot: VelocityControlBot
):
    # short sleep to allow the motors to accelerate a bit before the next command
    short_sleep = lambda: time.sleep(0.3)

    # very short sleep to add a short delay between motor commands
    very_short_sleep = lambda: time.sleep(0.05)
    short_sleep()

    velBot.go_forwards()

    while True:
        very_short_sleep()

        left_val = bot.get_left_touch_sensor_value()
        right_val = bot.get_right_touch_sensor_value()

        if left_val or right_val:
            velBot.stop()
            very_short_sleep()
            curse_print("We hit something")

            if left_val and right_val:
                curse_print("It was in front of us")
                posBot.move_backward()
                short_sleep()

                if random.randint(0, 100) % 2:
                    posBot.turn_left()
                    curse_print("We'll turn left")
                else:
                    posBot.turn_right()
                    curse_print("We'll turn right")
            elif left_val:
                curse_print("It was to our left, so we'll go back and turn right")
                posBot.move_backward()
                short_sleep()
                posBot.turn_right()
            elif right_val:
                curse_print("It was to our right, so we'll go back and turn left")
                posBot.move_backward()
                short_sleep()
                posBot.turn_left()

            short_sleep()
            posBot.wait_for_movement_completion()
            very_short_sleep()

            curse_print("And we'll start moving forward again")
            velBot.go_forwards()


def main():
    bot = PiBot()
    posControlBot = PositionControlBot(bot, 400)
    velControlBot = VelocityControlBot(bot, 200)

    control_loop(bot, posControlBot, velControlBot)


if __name__ == "__main__":
    main_wrapper(main)
