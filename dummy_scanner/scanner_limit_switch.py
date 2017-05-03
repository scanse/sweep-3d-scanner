"""Tests the limit switch"""
import time
import itertools


class LimitSwitch(object):
    """The limit switch."""

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
        # dummy does nothing

    def announce_push(self, channel):
        """Called when the switch is pressed"""
        print 'PUSHED on channel {}'.format(channel)

    def setup_event_detect(self):
        """Setup the switch to note press events."""
        # dummy does nothing

    def subscribe_to_press(self, callback):
        """Subscribe to a press event.
        :param callback: called when switch is pressed
        """
        # dummy does nothing

    def unsubscribe(self):
        """Remove event detection."""
        # dummy does nothing

    def is_pressed(self):
        """Checks if the switch is currently pressed"""
        # dummy returns False
        return False

    def check_for_press(self):
        """Returns true if an event was detected"""
        # dummy returns False
        return False

    def destroy(self):
        """Disable functionality.. useful on shutdown!"""
        # dummy does nothing


def main():
    """Creates a limit switch and prints a message when it is pressed"""
    print "Dummy has no main test"

if __name__ == '__main__':
    main()
