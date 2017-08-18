""" Dummy implementation of Adafruit_MotorHAT """
import time


class Adafruit_StepperMotor:
    """ Docstring """

    def __init__(self, controller, num, steps=200):
        """ Docstring """
        pass

    def setSpeed(self, rpm):
        """ Docstring """
        pass

    def oneStep(self, dir, style):
        """ Docstring """
        time.sleep(0.01)
        return 0

    def step(self, steps, direction, stepstyle):
        """ Docstring """
        time.sleep(0.01 * steps)


class Adafruit_DCMotor:
    """ Docstring """

    def __init__(self, controller, num):
        """ Docstring """
        pass

    def run(self, command):
        """ Docstring """
        pass

    def setSpeed(self, speed):
        """Docstring"""
        pass


class Adafruit_MotorHAT:
    """ Docstring """
    FORWARD = 1
    BACKWARD = 2
    BRAKE = 3
    RELEASE = 4

    SINGLE = 1
    DOUBLE = 2
    INTERLEAVE = 3
    MICROSTEP = 4

    def __init__(self, addr=None, freq=None, i2c=None, i2c_bus=None):
        """ Docstring """
        self.stepper = Adafruit_StepperMotor(None, None)
        self.motor = Adafruit_DCMotor(None, None)

    def setPin(self, pin, value):
        """ Docstring """
        pass

    def getStepper(self, steps, num):
        """ Docstring """
        return self.stepper

    def getMotor(self, num):
        """ Docstring """
        return self.motor
