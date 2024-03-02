# Project WALL-E
This repository contains code for the robotics tutorials for the 60019 Robotics module taught at Imperial in 2024.

The physical robot makes use of the BrickPi3 and LEGO sensors, but the code can be run without them, and is likely easily adapted to a different set of sensors and system by use of the `BotInterface` in `bot_control` and some modification of the `init_system` in `common.py`.

The group members were:
- [Ali Abbas](https://github.com/aliabbas299792)
- [Abrar Rashid](https://github.com/abrar-rashid)
- [Mohamed Ali](https://github.com/Mohamed-H-A)
- [Joshua Young](https://github.com/Josh13Young)
- [Wahbi Said](https://github.com/wahbzx)

## Robot Setup
Programs 1.0, 1.6.3, 2.2.1 and 2.2.2 work with the following setup:
- 2 motors with wheels on the side,
- 2 touch sensors for the left and right
- 1 forward facing ultrasonic sensor parallel to the ground on top
And the configuration of these (i.e setting ports) is in `bot_control/Bot.py`

Program 2.2.3 is similar, but the ultrasonic sensor isn't forward facing anymore

Programs 3.2.1, 3.2.2, 3.2.3 and 4.3 all use a forward facing ultrasonic sensor

## Dev Setup
Upon first cloning the repo, install `pre-commit` on your system (i.e on Ubuntu `sudo apt install pre-commit`) and run `pre-commit` in the root Git directory to initialise the git hooks we'll be using on this project.

We're also using `commitizen` for cleaner commit messages (`pip install commitizen`).
