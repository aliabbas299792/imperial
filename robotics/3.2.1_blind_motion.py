import math
import random
import time
from typing import List, Tuple

from bot_control.PositionControl import PositionControlBot
from common import WEB_PRINT, PiBot, main_wrapper

Particle = Tuple[float, float, float]
ParticleList = List[Particle]
Line = Tuple[float, float, float, float]


def drawParticles(ps: ParticleList):
    if WEB_PRINT:
        print(f"drawParticles:{ps}")


def drawLine(l: Line):
    if WEB_PRINT:
        print(f"drawLine:{l}")


def move_square_10(
    posControlBot: PositionControlBot, forward_dist=833, turn_amount=256
):
    square_lines = [
        (100, 100, 100, 600),
        (600, 600, 600, 100),
        (100, 600, 600, 600),
        (100, 100, 600, 100),
    ]

    for l in square_lines:
        drawLine(l)

    particles: ParticleList = [(100, 600, 0) for _ in range(100)]
    ten_cm = forward_dist / 4
    graph_10cm = 500 / 4
    drawParticles(particles)

    for _ in range(4):
        for _ in range(4):
            posControlBot.move_forward(ten_cm)

            for i in range(len(particles)):
                e = random.gauss(0, 0.02)
                f = random.gauss(0, 0.015)
                x, y, theta = particles[i]
                particle_new = (
                    x + (graph_10cm + e) * math.cos(theta),
                    y + (graph_10cm + f) * math.sin(theta),
                    theta,
                )
                particles[i] = particle_new

            drawParticles(particles)
            time.sleep(1.5)

        posControlBot.turn_left(turn_amount)
        for i in range(len(particles)):
            g = random.gauss(0, 0.01)
            x, y, theta = particles[i]

            particle_new = (x, y, theta - math.pi / 2 + g)

            particles[i] = particle_new

        drawParticles(particles)
        time.sleep(1.5)


def main():
    bot = PiBot()
    posControlBot = PositionControlBot(bot, 200)
    move_square_10(posControlBot, forward_dist=833, turn_amount=270)


if __name__ == "__main__":
    main_wrapper(main)
