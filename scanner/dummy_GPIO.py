""" Dummy version of GPIO """
from random import randint

BCM = 1
IN = 2
PUD_DOWN = 3
FALLING = 4
RELEASE = 5


def setmode(mode=None):
    """ Docstring """
    pass


def setup(pin=None, IO=None, pull_up_down=None):
    """ Docstring """
    pass


def add_event_detect(pin=None, edge=None, callback=None, bouncetime=None):
    """ Docstring """
    pass


def input(pin=None):
    """ Docstring """
    # simulates an input 10% of the time
    return randint(0, 10) < 1


def event_detected(pin=None):
    """ Docstring """
    # simulates an input 10% of the time
    return randint(0, 10) < 1


def remove_event_detect(pin=None):
    """ Docstring """
    pass
