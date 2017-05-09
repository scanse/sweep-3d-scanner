"""Tests the sweep's basic functions"""
import json
import sys
import traceback
from sweeppy import Sweep
import sweep_constants


def main():
    """Tests the sweep's basic functions"""
    try:
        with Sweep('/dev/ttyUSB0') as sweep:
            output_json_message(
                {'type': "update", 'status': "setup", 'msg': "Testing motor ready."})

            sweep.get_motor_ready()

            output_json_message(
                {'type': "update", 'status': "setup", 'msg': "Adjusting sample rate."})

            sweep.set_sample_rate(sweep_constants.SAMPLE_RATE_500_HZ)

            output_json_message(
                {'type': "update", 'status': "setup", 'msg': "Adjusting motor speed."})

            sweep.set_motor_speed(sweep_constants.MOTOR_SPEED_5_HZ)

            output_json_message(
                {'type': "update", 'status': "setup", 'msg': "Testing motor ready."})

            sweep.get_motor_ready()

            output_json_message(
                {'type': "update", 'status': "setup", 'msg': "Starting data acquisition."})

            sweep.start_scanning()

            output_json_message(
                {'type': "update", 'status': "setup", 'msg': "Stopping data acquisition."})

            sweep.stop_scanning()

            output_json_message(
                {'type': "update", 'status': "success", 'msg': "Done."})
    except:
        output_json_message({
            'type': "error",
            'status': "failed",
            'msg': 'Error during reset: {}'.format(traceback.format_exc())
        })
        exit(1)


def output_message(message):
    """Print the provided input & flush stdout so parent process registers the message"""
    print message
    sys.stdout.flush()


def output_json_message(json_input):
    """Print the provided json & flush stdout so parent process registers the message"""
    serialized_json = json.dumps(json_input, separators=(',', ':'))
    output_message(serialized_json)

if __name__ == '__main__':
    main()
