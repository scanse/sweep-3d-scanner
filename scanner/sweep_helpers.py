"""Defines constants and helper methods for the sweep device"""
from contextlib import contextmanager

MOTOR_SPEED_0_HZ = 0
MOTOR_SPEED_1_HZ = 1
MOTOR_SPEED_2_HZ = 2
MOTOR_SPEED_3_HZ = 3
MOTOR_SPEED_4_HZ = 4
MOTOR_SPEED_5_HZ = 5
MOTOR_SPEED_6_HZ = 6
MOTOR_SPEED_7_HZ = 7
MOTOR_SPEED_8_HZ = 8
MOTOR_SPEED_9_HZ = 9
MOTOR_SPEED_10_HZ = 10

SAMPLE_RATE_500_HZ = 500
SAMPLE_RATE_750_HZ = 750
SAMPLE_RATE_1000_HZ = 1000


@contextmanager
def create_sweep_w_error(port='/dev/ttyUSB0', use_dummy=False):
    """ Imports the appropriate library and tries to create a sweep.
        Catches and reports errors.
    """
    if use_dummy:
        from dummy_sweeppy import Sweep
    else:
        from sweeppy import Sweep

    try:
        with Sweep(port) as sweep:
            yield sweep, None
    except:
        yield None, "Failed to open sweep device."
