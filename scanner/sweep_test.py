"""Tests the sweep's basic functions"""
import time
import argparse
import sweep_helpers
from scanner_output import output_json_message


def main(arg_dict):
    """Tests the sweep's basic functions"""

    use_dummy = arg_dict['use_dummy']
    with sweep_helpers.create_sweep_w_error('/dev/ttyUSB0', use_dummy) as (sweep, err):
        if err:
            output_json_message(
                {'type': "update", 'status': "failed", 'msg': err})
            time.sleep(0.1)
            return

        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Testing motor ready."})

        sweep.get_motor_ready()

        time.sleep(0.1)
        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Adjusting sample rate."})

        sweep.set_sample_rate(sweep_helpers.SAMPLE_RATE_500_HZ)

        time.sleep(0.1)
        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Adjusting motor speed."})

        sweep.set_motor_speed(sweep_helpers.MOTOR_SPEED_5_HZ)

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
