"""Defines the rotating base of the scanner"""
import time
import atexit
import itertools
import argparse
from scanner_output import output_json_message

class ScannerBase(object):
    """The base of the 3d scanner (controls rotation via stepper motor).
    Attributes:
        motor_hat: default adafruit motor hat object
        stepper: the stepper motor
    """

    def __init__(self, stepper_steps_per_rev=None, stepper_motor_port=None, switch=None, use_dummy=False):
        """Return a ScannerBase object
        :param steps_per_rev: the number of steps per revolution
        :param motor_port:  the motor port #
        """
        # default to 400 steps/rev, motor port #1
        if stepper_steps_per_rev is None:
            stepper_steps_per_rev = 400
        if stepper_motor_port is None:
            stepper_motor_port = 2
        if switch is None:
            import scanner_limit_switch
            switch = scanner_limit_switch.LimitSwitch(use_dummy=use_dummy)

        # Import appropriate module
        if use_dummy:
            from dummy_Adafruit_MotorHAT import Adafruit_MotorHAT
        else:
            from Adafruit_MotorHAT import Adafruit_MotorHAT

        self.Adafruit_MotorHAT = Adafruit_MotorHAT

        # create a default object, no changes to I2C address or frequency
        self.motor_hat = self.Adafruit_MotorHAT()
        self.stepper = self.motor_hat.getStepper(
            stepper_steps_per_rev, stepper_motor_port)
        # default to 1 RPM (only used during reset)
        self.stepper.setSpeed(1)

        # note the limit switch
        self.switch = switch

        atexit.register(self.turn_off_motors)

    def move_steps(self, num_steps=None):
        """Moves the stepper motor the specified number of steps
        :param num_steps: # of steps to move, defaults to 1
        """
        if num_steps is None:
            num_steps = 1
        if num_steps < 0:
            num_steps = abs(num_steps)
            direction = self.Adafruit_MotorHAT.FORWARD
        else:
            direction = self.Adafruit_MotorHAT.BACKWARD

        for _ in itertools.repeat(None, num_steps):
            self.stepper.oneStep(direction, self.Adafruit_MotorHAT.MICROSTEP)

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

    def reset(self):
        """Resets the base angle."""
        # check that the switch is not already pressed
        # (edge case where a rising edge event won't occur)
        if not self.switch.is_pressed():
            # Move back to home angle, until hitting limit switch.
            self.switch.setup_event_detect()
            while not self.switch.check_for_press():
                # use DOUBLE mode for more torque
                self.stepper.step(2, self.Adafruit_MotorHAT.FORWARD,
                                  self.Adafruit_MotorHAT.DOUBLE)
            self.switch.destroy()

        # Move forward off the switch
        for _ in itertools.repeat(None, 12):
            self.stepper.step(1, self.Adafruit_MotorHAT.BACKWARD,
                              self.Adafruit_MotorHAT.DOUBLE)

        # check that the switch is not already pressed
        # (edge case where a rising edge event won't occur)
        if not self.switch.is_pressed():
            # Move back to home angle, until just hitting limit switch
            self.switch.setup_event_detect()
            while not self.switch.check_for_press():
                # use DOUBLE mode for more torque
                self.stepper.step(1, self.Adafruit_MotorHAT.FORWARD,
                                  self.Adafruit_MotorHAT.DOUBLE)
            self.switch.destroy()

    def turn_off_motors(self):
        """Turns off stepper motor, recommended for auto-disabling motors on shutdown!"""
        self.motor_hat.getMotor(1).run(self.Adafruit_MotorHAT.RELEASE)
        self.motor_hat.getMotor(2).run(self.Adafruit_MotorHAT.RELEASE)
        self.motor_hat.getMotor(3).run(self.Adafruit_MotorHAT.RELEASE)
        self.motor_hat.getMotor(4).run(self.Adafruit_MotorHAT.RELEASE)


def test_demo(use_dummy=False):
    """Performs a small test demo (reset, and move base 90 degrees)"""
    output_json_message(
        {'type': "update", 'status': "setup", 'msg': "Creating base!"})

    base = ScannerBase(use_dummy=use_dummy)

    # pause to avoid accidentally flushing the previous message contents
    time.sleep(0.1)

    output_json_message(
        {'type': "update", 'status': "progress", 'msg': "Resetting base..."})

    base.reset()

    output_json_message(
        {'type': "update", 'status': "progress", 'msg': "Moving base 90 degrees..."})

    for _ in itertools.repeat(None, 90):
        base.move_degrees(1)
        time.sleep(.1)  # sleep for 100 ms

    output_json_message(
        {'type': "update", 'status': "complete", 'msg': "Finished test!"})


def main(arg_dict):
    """Creates a base and moves it 90 degrees"""
    test_demo(use_dummy=arg_dict['use_dummy'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Creates a 3D scanner base and performs a test')

    parser.add_argument('-d', '--use_dummy',
                        help='Use the dummy verison without hardware',
                        default=False,
                        action='store_true',
                        required=False)

    args = parser.parse_args()
    argsdict = vars(args)

    main(argsdict)
