"""Defines the rotating base of the scanner"""
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import time
import atexit
import itertools


class ScannerBase(object):
    """The base of the 3d scanner (controls rotation via stepper motor).
    Attributes:
        motor_hat: default adafruit motor hat object
        stepper: the stepper motor
    """

    def __init__(self, stepper_steps_per_rev=None, stepper_motor_port=None):
        """Return a ScannerBase object
        :param steps_per_rev: the number of steps per revolution
        :param motor_port:  the motor port #
        """
        # default to 200 steps/rev, motor port #1
        if stepper_steps_per_rev is None:
            stepper_steps_per_rev = 400
        if stepper_motor_port is None:
            stepper_motor_port = 2

        # create a default object, no changes to I2C address or frequency
        self.motor_hat = Adafruit_MotorHAT()
        self.stepper = self.motor_hat.getStepper(
            stepper_steps_per_rev, stepper_motor_port)

        atexit.register(self.turn_off_motors)

    def move_steps(self, num_steps=None):
        """Moves the stepper motor the specified number of steps
        :param num_steps: # of steps to move, defaults to 1
        """
        if num_steps is None:
            num_steps = 1
        for _ in itertools.repeat(None, num_steps):
            self.stepper.oneStep(Adafruit_MotorHAT.BACKWARD,
                                 Adafruit_MotorHAT.MICROSTEP)

    def move_degrees(self, num_deg=None):
        """Moves the stepper motor by the specified num_deg, as close as step resolution permits.
        :param num_deg: angle to move in degrees, defaults to 1 degree
        """
        if num_deg is None:
            num_deg = 1
        self.move_steps(int(round(num_deg * self.get_steps_per_deg())))

    def get_num_steps_per_rev(self):
        """Returns the number of micro-steps in a full rotation"""
        return 400 * 8  # 400 steps/rev * 8 microsteps/step

    def get_steps_per_deg(self):
        """Returns the number of steps per degree"""
        return 1.0 * self.get_num_steps_per_rev() / 360.0

    def turn_off_motors(self):
        """Turns off stepper motor, recommended for auto-disabling motors on shutdown!"""
        self.motor_hat.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        self.motor_hat.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self.motor_hat.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self.motor_hat.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


def main():
    """Creates a base and moves it 90 degrees"""
    print "Creating base..."
    base = ScannerBase()

    print base.get_steps_per_deg()

    print "Moving base 90 degrees..."
    for _ in itertools.repeat(None, 90):
        base.move_degrees(1)
        time.sleep(.1)  # sleep for 100 ms

    print "Done!"

if __name__ == '__main__':
    main()
