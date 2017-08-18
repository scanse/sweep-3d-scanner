"""Tests the sweep's basic functions"""
import json
import sys
import time
import argparse
import sweep_constants


def output_message(message):
    """Print the provided input & flush stdout so parent process registers the message"""
    print message
    sys.stdout.flush()


def output_json_message(json_input):
    """Print the provided json & flush stdout so parent process registers the message"""
    serialized_json = json.dumps(json_input, separators=(',', ':'))
    output_message(serialized_json)


def main(arg_dict):
    """Tests the sweep's basic functions"""

    # import the appropriate modules
    if arg_dict['use_dummy']:
        from dummy_sweeppy import Sweep
    else:
        from sweeppy import Sweep

    with Sweep('/dev/ttyUSB0') as sweep:
        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Testing motor ready."})

        sweep.get_motor_ready()

        time.sleep(0.1)
        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Adjusting sample rate."})

        sweep.set_sample_rate(sweep_constants.SAMPLE_RATE_500_HZ)

        time.sleep(0.1)
        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Adjusting motor speed."})

        sweep.set_motor_speed(sweep_constants.MOTOR_SPEED_5_HZ)

        time.sleep(0.1)
        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Testing motor ready."})

        sweep.get_motor_ready()

        time.sleep(0.1)
        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Starting data acquisition."})

        sweep.start_scanning()
        time.sleep(0.1)

        desired_num_sweeps = 3
        for scan_count, scan in enumerate(sweep.get_scans()):
            # note that a scan was received (used to avoid the timeout)
            output_json_message(
                {'type': "update", 'status': "setup", 'msg': "Received Scan."})
            if scan_count == desired_num_sweeps:
                break

        time.sleep(0.1)
        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Stopping data acquisition."})

        sweep.stop_scanning()

        time.sleep(0.1)
        output_json_message(
            {'type': "update", 'status': "complete", 'msg': "Finished Test!"})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Creates a Sweep object and performs a test')

    parser.add_argument('-d', '--use_dummy',
                        help='Use the dummy verison without hardware',
                        default=False,
                        action='store_true',
                        required=False)

    args = parser.parse_args()
    argsdict = vars(args)

    main(argsdict)
