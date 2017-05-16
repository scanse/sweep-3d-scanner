"""Releases any stepper motors"""
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import sys
import json


def output_message(message):
    """Print the provided input & flush stdout so parent process registers the message"""
    print message
    sys.stdout.flush()


def output_json_message(json_input):
    """Print the provided json & flush stdout so parent process registers the message"""
    serialized_json = json.dumps(json_input, separators=(',', ':'))
    output_message(serialized_json)


def main():
    """Releases any stepper motors"""
    motor_hat = Adafruit_MotorHAT()
    motor_hat.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    motor_hat.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    motor_hat.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    motor_hat.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

    output_json_message(
        {'type': "update", 'status': "complete", 'msg': "Released Stepper Motors!"})

if __name__ == '__main__':
    main()
