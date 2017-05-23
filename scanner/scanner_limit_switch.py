"""Tests the limit switch"""
import RPi.GPIO as GPIO
import time
import atexit
import itertools
import sys
import json


class LimitSwitch(object):
    """The limit switch.
    Attributes:
        pin: the GPIO pin for the limit switch
    """

    def __init__(self, pin=None, debounce_ms=None):
        """Return a LimitSwitch object
        :param pin: the GPIO pin
        """
        # default to pin #17
        if pin is None:
            pin = 17
        # default to debounce duration 100ms
        if debounce_ms is None:
            debounce_ms = 100

        self.pin = pin
        self.debounce_ms = debounce_ms

        # Setup the switch
        GPIO.setmode(GPIO.BCM)
        # Configure on provided pin as...
        # input with internal pull down resistor (for Normally Closed switch)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # make sure there are no prior events ?
        self.unsubscribe()

        atexit.register(self.destroy)

    def announce_push(self, channel):
        """Called when the switch is pressed"""
        print 'PUSHED on channel {}'.format(channel)

    def setup_event_detect(self):
        """Setup the switch to note press events."""
        self.destroy()
        # add falling edge detection on the pin (in the normally closed case it comes first)
        # bouncetime ms (debouncing)
        GPIO.add_event_detect(self.pin, GPIO.FALLING,
                              bouncetime=self.debounce_ms)

    def subscribe_to_press(self, callback):
        """Subscribe to a press event.
        :param callback: called when switch is pressed
        """
        # remove any existing subscription
        self.destroy()
        # Setup Callback
        # add falling edge detection on the pin (in the normally closed case it comes first)
        # bouncetime ms (debouncing)
        GPIO.add_event_detect(self.pin, GPIO.FALLING,
                              callback=callback, bouncetime=self.debounce_ms)

    def unsubscribe(self):
        """Remove event detection."""
        GPIO.remove_event_detect(self.pin)

    def is_pressed(self):
        """Checks if the switch is currently pressed"""
        return not GPIO.input(self.pin)

    def check_for_press(self):
        """Returns true if an event was detected"""
        return GPIO.event_detected(self.pin)

    def destroy(self):
        """Disable functionality.. useful on shutdown!"""
        self.unsubscribe()


def output_message(message):
    """Print the provided input & flush stdout so parent process registers the message"""
    print message
    sys.stdout.flush()


def output_json_message(json_input):
    """Print the provided json & flush stdout so parent process registers the message"""
    serialized_json = json.dumps(json_input, separators=(',', ':'))
    output_message(serialized_json)


def test_demo():
    """Performs a small test demo (prints message when switch is pressed)"""
    output_json_message({'type': "update", 'status': "instruction",
                         'msg': "Try pressing the limit switch... You have 10 seconds."})
    # pause... give time for user to read directions
    time.sleep(.5)

    switch = LimitSwitch(17)

    # run for 10 seconds
    for _ in itertools.repeat(None, 100):
        time.sleep(.1)
        if switch.is_pressed():
            output_json_message(
                {'type': "update", 'status': "progress", 'msg': "Pressed!"})

    # pause to avoid accidentally flushing the previous message contents
    time.sleep(0.1)

    output_json_message(
        {'type': "update", 'status': "complete", 'msg': "Finished test!"})


def main():
    """Creates a limit switch and prints a message when it is pressed"""
    test_demo()

if __name__ == '__main__':
    main()
