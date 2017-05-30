"""Helpful cleanup methods for the scanner"""
import argparse
import sys
import json
import time


def idle_sweep():
    """Stops any active stream and sets the sweep to idle"""
    time.sleep(0.1)
    output_json_message(
        {'type': "update", 'status': "progress", 'msg': "Set sweep to idle!"})
    time.sleep(0.1)


def release_motors():
    """Releases any stepper motors"""
    time.sleep(0.1)
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

    parser.add_argument('--release_motor',
                        help='Release any active motors (True/False)',
                        default=False,
                        required=False,
                        action='store_true')
    parser.add_argument('--idle_sweep',
                        help='Sets the sweep motor to idle (0Hz)',
                        default=False,
                        required=False,
                        action='store_true')

    args = parser.parse_args()
    argsdict = vars(args)

    main(argsdict)
