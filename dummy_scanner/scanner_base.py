"""Defines the rotating base of the scanner"""
import time
import itertools


class ScannerBase(object):
    """The base of the 3d scanner (controls rotation via stepper motor)."""

    def __init__(self, stepper_steps_per_rev=None, stepper_motor_port=None, switch=None):
        """Return a ScannerBase object
        :param steps_per_rev: the number of steps per revolution
        :param motor_port:  the motor port #
        """
        # default to 400 steps/rev, motor port #1
        if stepper_steps_per_rev is None:
            stepper_steps_per_rev = 400

    def move_steps(self, num_steps=None):
        """Moves the stepper motor the specified number of steps
        :param num_steps: # of steps to move, defaults to 1
        """
        # do nothing

    def move_degrees(self, num_deg=None):
        """Moves the stepper motor by the specified num_deg, as close as step resolution permits.
        :param num_deg: angle to move in degrees, defaults to 1 degree
        """
        # do nothing

    def get_num_steps_per_rev(self):
        """Returns the number of micro-steps in a full rotation"""
        return 400 * 8  # 400 steps/rev * 8 microsteps/step

    def get_steps_per_deg(self):
        """Returns the number of steps per degree"""
        return 1.0 * self.get_num_steps_per_rev() / 360.0

    def reset(self):
        """Resets the base angle."""
        # simulate moving backward toward home position, until hitting the
        # limit switch
        time.sleep(4.0)

        # simulate moving forward off the switch
        time.sleep(1.5)


def test_demo():
    """Performs a small test demo (reset, and move base 90 degrees)"""
    base = ScannerBase()
    base.reset()
    for _ in itertools.repeat(None, 90):
        base.move_degrees(1)
        time.sleep(.1)  # sleep for 100 ms


def main():
    """Creates a base and moves it 90 degrees"""
    test_demo()


if __name__ == '__main__':
    main()
