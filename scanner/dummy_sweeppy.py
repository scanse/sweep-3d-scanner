"""Dummy implementation of sweeppy library methods/classes"""
import collections
import time
import sweep_helpers


class Scan(collections.namedtuple('Scan', 'samples')):
    """A collection of sensor readings"""
    pass


class Sample(collections.namedtuple('Sample', 'angle distance signal_strength')):
    """A single sensor reading, comprised of an angle, distance and signal strength"""
    pass


class Sweep(object):
    """ Dummy implementation of Sweep """

    def __init__(self, port, bitrate=None):
        self.motor_speed = sweep_helpers.MOTOR_SPEED_1_HZ
        self.sample_rate = sweep_helpers.SAMPLE_RATE_500_HZ

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def start_scanning(self):
        """ Docstring """
        time.sleep(2.0)

    def stop_scanning(self):
        """ Docstring """
        time.sleep(0.5)

    def get_motor_ready(self):
        """ Docstring """
        time.sleep(0.1)
        return True

    def get_motor_speed(self):
        """ Docstring """
        time.sleep(0.1)
        return self.motor_speed

    def set_motor_speed(self, speed):
        """ Docstring """
        time.sleep(0.1)
        self.motor_speed = speed

    def get_sample_rate(self):
        """ Docstring """
        time.sleep(0.1)
        return self.sample_rate

    def set_sample_rate(self, speed):
        """ Docstring """
        self.sample_rate = speed
        time.sleep(0.1)

    def get_scans(self):
        """ Coroutine-based generator lazily returning the same dummy scan ad infinitum"""
        while True:
            time.sleep(1.0 / self.motor_speed)
            spacing = 360.0 / self.sample_rate
            dummy_samples = [Sample(angle=1000 * spacing * n, distance=1000, signal_strength=199)
                             for n in range(self.sample_rate)]
            yield Scan(samples=dummy_samples)

    def reset(self):
        """ Docstring """
        time.sleep(2.0)
