import math
import random
import time
from dataclasses import dataclass
from typing import Tuple

from bot_control.PositionControl import PositionControlBot
from common import PiBot, curse_print, main_wrapper
from provided_code.particleDataStructures import canvas, mymap

STANDARD_SLEEP_AMOUNT = 1.5
MAX_ANGLE_FROM_WALL_NORMAL = 15


class Positions:
    # Holds the particles and weights
    def __init__(self):
        self.particles = [(float(84), float(30), float(0)) for _ in range(100)]
        self.weights = [1 / len(self.particles) for _ in range(len(self.particles))]

    # Draws all particles
    def draw(self):
        canvas.drawParticles(self.particles)

    # Calculates new nx, ny, ntheta of the robot
    def get_new_avg_pos(self):
        x_bar = sum(
            [self.weights[i] * self.particles[i][0] for i in range(len(self.particles))]
        )
        y_bar = sum(
            [self.weights[i] * self.particles[i][1] for i in range(len(self.particles))]
        )
        theta_bar = sum(
            [self.weights[i] * self.particles[i][2] for i in range(len(self.particles))]
        )
        return x_bar, y_bar, theta_bar

    def normalise(self):
        new_weights = []
        total = sum(self.weights)
        for weight in self.weights:
            new_weights.append(weight / total)
        self.weights = new_weights

    def resample(self):  # Follows spec method
        n = len(self.particles)
        new_particles = []
        # Build cumulative weights array
        cumulative_weights = [sum(self.weights[: i + 1]) for i in range(n)]
        # Generate new particles
        for _ in range(n):
            random_number = random.random()
            # Find the index in the cumulative weights array where the random number falls
            for i in range(n):
                if random_number <= cumulative_weights[i]:
                    new_particles.append(self.particles[i])
                    break

        self.particles = new_particles

        # Resets weights to all be equal because after resampling each particle should have an equal chance of being selected
        self.weights = [1 / len(self.particles) for _ in range(len(self.particles))]


################## Program State ##################


@dataclass
class MCLProgramState:
    # Contains the shared state of the program

    # All the walls of the arena
    walls = {
        1: ((210, 84), (210, 0)),
        2: ((168, 84), (210, 84)),
        3: ((0, 0), (0, 168)),
        4: ((84, 210), (168, 210)),
        5: ((84, 126), (84, 210)),
        6: ((210, 0), (0, 0)),
        7: ((0, 0), (0, 168)),
        8: ((210, 0), (0, 0)),
    }

    positions = Positions()
    positionControlBot = PositionControlBot(PiBot())


### Aliases ###

posBot = MCLProgramState.positionControlBot
positions = MCLProgramState.positions
walls = MCLProgramState.walls


################## Code ##################


def calc_angle_from_wall_normal(theta, wall):
    (a_x, a_y), (b_x, b_y) = wall
    num = (math.cos(theta)) * (a_y - b_y) + (math.sin(theta)) * (b_x - a_x)
    den = math.sqrt((a_y - b_y) ** 2 + (b_x - a_x) ** 2)

    return math.acos(num / den)


def distance(point1: Tuple[float, float], point2: Tuple[float, float]):
    x_1, y_1 = point1
    x_2, y_2 = point2
    return math.sqrt((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2)


# Forward distance between the robot and a wall
def wall_dist(x, y, theta, wall):
    a, b = wall
    (a_x, a_y) = a
    (b_x, b_y) = b

    q = (b_y - a_y) * (math.cos(theta))
    r = (b_x - a_x) * (math.sin(theta))
    if (q - r) == 0:
        return math.inf
    m = ((b_y - a_y) * (a_x - x) - (b_x - a_x) * (a_y - y)) / (q - r)

    offset_x = x + m * math.cos(theta)
    offset_y = y + m * math.sin(theta)
    o = (offset_x, offset_y)

    lb_x, ub_x = sorted([a_x, b_x])
    lb_y, ub_y = sorted([a_y, b_y])

    # reason for errors was floating point errors, i.e 0 <= -0.00000000001 <= 0 isn't true
    if lb_x <= round(offset_x, 6) <= ub_x and lb_y <= round(offset_y, 6) <= ub_y:
        return m

    return math.inf


# Returns the distance to the closest wall and the wall which robot should be facing
def find_dist_to_closest_wall(x, y, theta) -> Tuple[float, Tuple[float, float]]:
    min_m = float("inf")
    min_wall = None

    ms = []
    for wall in walls.values():

        m = wall_dist(x, y, theta, wall)
        ms.append(m)
        if m < 0:
            continue
        if m < min_m and m < math.inf:
            min_m = m
            min_wall = wall

    if min_wall is None:
        curse_print(x, y, theta)
        raise ValueError(
            "Robot is not facing any wall. Enclosed arena assumption violated."
        )

    return min_m, min_wall


def calculate_likelihood(x, y, theta, z):
    sigma = 0.02
    K = 0.1
    m, _ = find_dist_to_closest_wall(x, y, theta)
    return math.exp((-((-z - m) ** 2)) / (2 * sigma**2)) + K


def mcl_update(was_turn, x, y, theta, distance, angle):
    sonars = [posBot.bot.get_ultrasonic_sensor_value() for _ in range(10)]
    sonar = sum(sonars) / len(sonars)  # Avg sonar readings

    # Skip all weight/MCL updates if angle to closest wall normal is too small
    _, wall = find_dist_to_closest_wall(x, y, theta)
    skip_update = calc_angle_from_wall_normal(theta, wall) > MAX_ANGLE_FROM_WALL_NORMAL
    new_particles = []
    if not was_turn:  # Do random gauss + likelihood for forward motion
        for i in range(len(positions.particles)):
            e = random.gauss(0, 0.02)
            f = random.gauss(0, 0.015)
            th = positions.particles[i][2]
            lst = list(positions.particles[i])
            lst[0] += (distance + e) * math.cos(th)
            lst[1] += (distance + e) * math.sin(th)
            lst[2] += f
            particle = tuple(lst)
            new_particles.append(particle)

            if not skip_update:
                likelihood = calculate_likelihood(lst[0], lst[1], lst[2], sonar)
                positions.weights[i] = likelihood * positions.weights[i]
    else:
        # Do random gauss + likelihood for turning motion
        for i in range(len(positions.particles)):
            g = random.gauss(0, 0.01)
            lst = list(positions.particles[i])
            lst[2] += angle + g
            particle = tuple(lst)
            new_particles.append(particle)

            if not skip_update:
                likelihood = calculate_likelihood(lst[0], lst[1], lst[2], sonar)
                positions.weights[i] = likelihood * positions.weights[i]

    positions.particles = new_particles

    if not skip_update:
        positions.normalise()
        positions.resample()

    positions.draw()
    return positions.get_new_avg_pos()


def move_robot(x, y, theta, wx, wy):
    # Moves robot 20cm/remainder of drive amount
    # Does the 4 MCL update steps

    centimeter = 833 / 40
    rotate = 1080

    x_new, y_new = wx - x, wy - y
    angle = (math.atan2(y_new, x_new)) - theta
    dist = math.sqrt(x_new**2 + y_new**2)
    motorDriveAmount = (
        centimeter * dist
    )  # How much the wheels turn to reach the waypoint forward

    if angle < -math.pi:
        angle += math.tau
    elif angle > math.pi:
        angle -= math.tau
    motorTurnAmount = rotate * (angle / math.tau)

    posBot.turn_left(motorTurnAmount)
    nx, ny, ntheta = mcl_update(True, x, y, theta, 0, angle)
    time.sleep(STANDARD_SLEEP_AMOUNT)

    # Move 20 else the remainder
    if motorDriveAmount > centimeter * 20:
        motionAmount = centimeter * 20
        dist = 20
    else:
        motionAmount = motorDriveAmount

    posBot.move_forward(motionAmount)
    time.sleep(STANDARD_SLEEP_AMOUNT)
    nnx, nny, nntheta = mcl_update(False, nx, ny, ntheta, dist, 0)
    curse_print(
        f"New position: ({nnx}, {nny}, {math.degrees(nntheta)}), desired position: ({wx}, {wy}, any)"
    )
    return (
        nnx,
        nny,
        nntheta,
    )


def navigateToWaypoint(x, y, theta, wx, wy):
    # Continuously moves robot towards given waypoint until within threshhold distance
    threshhold = 1  # Used to decide whether to keep moving towards waypoint
    nx, ny, ntheta = move_robot(x, y, theta, wx, wy)
    while distance((nx, ny), (wx, wy)) > threshhold:
        nx, ny, ntheta = move_robot(nx, ny, ntheta, wx, wy)
    return nx, ny, ntheta


def navigateToAllWaypoints(x, y, theta):
    # Moves robot to all waypoints
    curse_print(f"Starting at: ({x}, {y}, {theta})")
    waypoints = [
        (180, 30),
        (180, 54),
        (138, 54),
        (138, 168),
        (114, 168),
        (114, 84),
        (84, 84),
        (84, 30),
    ]

    nx, ny, ntheta = x, y, theta

    for wx, wy in waypoints:
        curse_print(f"Going towards new waypoint: ({wx}, {wy}, any)")
        nx, ny, ntheta = navigateToWaypoint(nx, ny, ntheta, wx, wy)
        time.sleep(STANDARD_SLEEP_AMOUNT)


def main():
    posBot.bot.set_motor_limits(35)

    mymap.draw()
    waypoint1 = (84, 30, 0)
    navigateToAllWaypoints(waypoint1[0], waypoint1[1], waypoint1[2])


if __name__ == "__main__":
    main_wrapper(main)
