"""Dummy implementation of a few sweeppy library methods/classes"""
import collections
import time


class Scan(collections.namedtuple('Scan', 'samples')):
    """A collection of sensor readings"""
    pass


class Sample(collections.namedtuple('Sample', 'angle distance signal_strength')):
    """A single sensor reading, comprised of an angle, distance and signal strength"""
    pass


def get_scans():
    """coroutine-based generator lazily returning the same dummy scan ad infinitum"""
    while True:
        time.sleep(1.0)
        dummy_samples = [Sample(angle=1000 * 5 * n, distance=1000, signal_strength=199)
                         for n in range(72)]
        yield Scan(samples=dummy_samples)
