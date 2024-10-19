import math
import time
from dataclasses import dataclass

from bot_control.PositionControl import PositionControlBot
from common import PiBot, curse_echo, curse_getstr, curse_print, main_wrapper

MOTOR_LIMIT = 50
EMPIRICAL_METRE = int((833 / 4) * 10)
EMPIRICAL_ROTATE = 1080


@dataclass
class RobotVector:
    x: float = 0
    y: float = 0
    thetaDeg: float = 0

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normaliseAngle(self):
        if self.thetaDeg < -180:
            self.thetaDeg += 360
        elif self.thetaDeg > 180:
            self.thetaDeg -= 360


def navigateToWaypoint(
    posControlBot: PositionControlBot, state: RobotVector, wx: float, wy: float
):
    moveVec = RobotVector(wx - state.x, wy - state.y)
    moveVec.thetaDeg = math.degrees(math.atan2(moveVec.y, moveVec.x)) - state.thetaDeg
    dist = moveVec.magnitude()
    moveVec.normaliseAngle()

    motorDriveAmount = EMPIRICAL_METRE * dist
    motorTurnAmount = EMPIRICAL_ROTATE * (moveVec.thetaDeg / 360)
    curse_print("Robot angle: " + str(moveVec.thetaDeg))

    posControlBot.turn_left(motorTurnAmount)
    time.sleep(2)

    posControlBot.move_forward(motorDriveAmount)
    time.sleep(4)

    return RobotVector(wx, wy, state.thetaDeg + moveVec.thetaDeg)


def control_loop_body(posControlBot: PositionControlBot, state: RobotVector):
    curse_print("Waypoint coordinate in format: x,y")
    curse_echo(True)
    line = curse_getstr()
    curse_echo(False)

    x_str, y_str = map(str.strip, line.split(","))
    inp_x = float(x_str)
    inp_y = float(y_str)
    curse_print(f"Moving to ({inp_x}, {inp_y})")
    return navigateToWaypoint(posControlBot, state, inp_x, inp_y)


def main():
    state = RobotVector()
    bot = PiBot()
    bot.set_motor_limits(MOTOR_LIMIT)
    posControlBot = PositionControlBot(bot)

    while True:
        state = control_loop_body(posControlBot, state)
        time.sleep(0.1)


if __name__ == "__main__":
    main_wrapper(main)
