"""Helpful cleanup methods for the scanner"""
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
from sweeppy import Sweep
import sweep_constants
import argparse
import sys
import json
import time


def idle_sweep():
    """Stops any active stream and sets the sweep to idle"""
    # device construction involves stopping any active data streams
    with Sweep('/dev/ttyUSB0') as sweep:
        sweep.set_motor_speed(sweep_constants.MOTOR_SPEED_0_HZ)
        output_json_message(
            {'type': "update", 'status': "progress", 'msg': "Set sweep to idle!"})
        time.sleep(0.1)


def release_motors():
    """Releases any stepper motors"""
    motor_hat = Adafruit_MotorHAT()
    motor_hat.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    motor_hat.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    motor_hat.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    motor_hat.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
    output_json_message(
        {'type': "update", 'status': "progress", 'msg': "Released Stepper Motors!"})
    time.sleep(0.1)


def output_message(message):
    """Print the provided input & flush stdout so parent process registers the message"""
    print message
    sys.stdout.flush()


def output_json_message(json_input):
    """Print the provided json & flush stdout so parent process registers the message"""
    serialized_json = json.dumps(json_input, separators=(',', ':'))
    output_message(serialized_json)


def main(arg_dict):
    """Perform any requested routines"""
    if arg_dict['release_motor'] is True:
        release_motors()
    if arg_dict['idle_sweep'] is True:
        idle_sweep()

    output_json_message(
        {'type': "update", 'status': "complete", 'msg': "Tasks completed successfully!"})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Performs various helper methods on a scan')

    parser.add_argument('-rm', '--release_motor',
                        help='Release any active motors (True/False)',
                        default=False,
                        required=False)
    parser.add_argument('-i', '--idle_sweep',
                        help='Sets the sweep motor to idle (0Hz)',
                        default=False,
                        required=False)

    args = parser.parse_args()
    argsdict = vars(args)

    main(argsdict)
