"""Defines a 3D scanner"""
from sweeppy import Sweep
import sweep_constants


def main():
    """Sets the sweep to idle"""
    with Sweep() as sweep:
        sweep.set_motor_speed(sweep_constants.MOTOR_SPEED_0_HZ)

if __name__ == '__main__':
    main()
