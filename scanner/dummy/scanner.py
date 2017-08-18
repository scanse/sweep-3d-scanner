"""Defines a 3D scanner"""
import dummy_sweeppy
import sweep_constants
import scan_settings
import scanner_base
import scan_exporter
import scan_utils
import time
import datetime
import math
import atexit
import sys
import argparse
import json


class Scanner(object):
    """The 3d scanner.
    Attributes:
        base: the rotating base
        settings: the scan settings
        exporter: the scan exporter
    """

    def __init__(self, device=None, base=None, settings=None, exporter=None):
        """Return a Scanner object
        :param base:  the scanner base
        :param device: the sweep device
        :param settings: the scan settings
        :param exporter: the scan exporter
        """
        if base is None:
            base = scanner_base.ScannerBase()
        if settings is None:
            settings = scan_settings.ScanSettings()
        if exporter is None:
            exporter = scan_exporter.ScanExporter()

        self.base = base
        self.settings = settings
        self.exporter = exporter

    def setup_base(self):
        """Setup the base"""
        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Resetting base to home position."})
        self.base.reset()

    def setup_device(self):
        """Setup the device"""
        reset_max_duration = 11.0

        output_json_message({'type': "update", 'status': "setup",
                             'msg': "Resetting device.", 'duration': reset_max_duration})

        # Reset the device
        # dummy does nothing

        # sleep for at least the minimum time required to reset the device
        time.sleep(reset_max_duration)

        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Adjusting device settings."})

        # Set the sample rate
        # Dummy does nothing
        time.sleep(0.05)

        # Set the motor speed
        # Dummy does nothing
        time.sleep(0.05)

    def setup(self):
        """Setup the scanner according to the scan settings"""
        # setup the device, wait for it to calibrate
        self.setup_device()

        # wait until the device is ready, so as not to disrupt the calibration
        # dummy waits 8 seconds (16 x 0.5 seconds)
        for x in range(0, 16):
            # Convey that the motor speed is still adjusting
            output_json_message({'type': "update", 'status': "setup",
                                 'msg': "Waiting for calibration routine and motor speed to stabilize."})

            time.sleep(0.5)

        # setup the base
        self.setup_base()

    def idle(self):
        """Stops the device from spinning"""
        # dummy does nothing
        time.sleep(0.1)

    def perform_scan(self):
        """Performs a complete 3d scan
        :param angular_range: the angular range for the base to cover during the scan (default 180)
        """
        # Calcualte the # of evenly spaced 2D sweeps (base movements) required
        # to match resolutions
        num_sweeps = int(round(self.settings.get_resolution()
                               * self.settings.get_scan_range()))

        # Caclulate the number of stepper steps covering the angular range
        num_stepper_steps = self.settings.get_scan_range() * self.base.get_steps_per_deg()

        # Calculate number of stepper steps per move (ie: between scans)
        num_stepper_steps_per_move = int(round(num_stepper_steps / num_sweeps))

        # Actual angle per move (between individual 2D scans)
        angle_between_sweeps = 1.0 * num_stepper_steps_per_move / \
            self.base.get_steps_per_deg()

        # correct the num_sweeps to account for the accumulated difference due
        # to rounding
        num_sweeps = math.floor(
            1.0 * self.settings.get_scan_range() / angle_between_sweeps)

        # add 2 to account for gap from splitting each scan
        num_sweeps = num_sweeps + 2

        output_json_message({
            'type': "update",
            'status': "scan",
            'msg': "Initiating scan...",
            'duration': num_sweeps / self.settings.get_motor_speed(),
            'remaining': num_sweeps / self.settings.get_motor_speed()
        })

        # Start Scanning
        # dummy waits 6 seconds
        time.sleep(6.0)

        valid_scan_index = 0
        arrival_time = 0
        time_until_deadzone = 0
        rotated_already = False

        # get_scans is coroutine-based generator lazily returning scans ad
        # infinitum
        for scan_count, scan in enumerate(dummy_sweeppy.get_scans()):
            # note the arrival time
            arrival_time = time.time()

            # remove readings from unreliable distances
            scan_utils.remove_distance_extremes(
                scan, self.settings.get_min_range_val(), self.settings.get_max_range_val())

            # Remove readings from the deadzone
            scan_utils.remove_angular_window(
                scan, self.settings.get_deadzone(), 360 - self.settings.get_deadzone())

            if valid_scan_index >= num_sweeps - 2:
                # Avoid redundant data in last few partially overlapping scans
                scan_utils.remove_angular_window(
                    scan, self.settings.get_deadzone(), 361)

            # Catch scans that contain unordered samples, and discard them
            # (this may indicate problem reading sync byte)
            if scan_utils.contains_unordered_samples(scan):
                continue

            # Edge case (discard 1st scan without base movement and move base)
            if not rotated_already:
                # Wait for the device to reach the threshold angle for movement
                time_until_deadzone = self.settings.get_time_to_deadzone_sec() - \
                    (time.time() - arrival_time)
                if time_until_deadzone > 0:
                    time.sleep(time_until_deadzone)

                # Move the base
                self.base.move_steps(num_stepper_steps_per_move)
                rotated_already = True
                continue

            # Export the scan
            self.exporter.export_2D_scan(
                scan,
                valid_scan_index,
                self.settings.get_mount_angle(),
                angle_between_sweeps * valid_scan_index,          # base angle before move
                # base angle after move
                angle_between_sweeps * (valid_scan_index + 1),
                False
            )

            # increment the scan index
            valid_scan_index = valid_scan_index + 1

            # Wait for the device to reach the threshold angle for movement
            time_until_deadzone = self.settings.get_time_to_deadzone_sec() - \
                (time.time() - arrival_time)
            if time_until_deadzone > 0:
                time.sleep(time_until_deadzone)

            # Move the base
            self.base.move_steps(num_stepper_steps_per_move)

            output_json_message({
                'type': "update",
                'status': "scan",
                'msg': "Scan in Progress...",
                'duration': num_sweeps / self.settings.get_motor_speed(),
                'remaining': (num_sweeps - valid_scan_index) / self.settings.get_motor_speed()
            })

            # Collect the appropriate number of 2D scans
            if valid_scan_index >= num_sweeps:
                break

        # Stop scanning
        # dummy does nothing
        time.sleep(0.05)

        output_json_message({
            'type': "update",
            'status': "complete",
            'msg': "Finished scan!"
        })

    def shutdown(self, msg=None):
        """Print message and shutdown"""
        exit()

    def get_base(self):
        """Returns the ScannerBase object for this scanner"""
        return self.base

    def set_base(self, base=None):
        """Sets the base for this scanner to the provided ScannerBase object"""
        if base is None:
            base = scanner_base.ScannerBase()
        self.base = base

    def get_settings(self):
        """Returns the scan settings for this scanner"""
        return self.settings

    def set_settings(self, settings=None):
        """Sets the scan settings for this scanner to the provided ScanSettings object"""
        if settings is None:
            settings = scan_settings.ScanSettings()
        self.settings = settings


def output_message(message):
    """Print the provided input & flush stdout so parent process registers the message"""
    print message
    sys.stdout.flush()


def output_json_message(json_input):
    """Print the provided json & flush stdout so parent process registers the message"""
    serialized_json = json.dumps(json_input, separators=(',', ':'))
    output_message(serialized_json)


def main(arg_dict):
    """Creates a 3D scanner and gather a scan"""
    # Create a scan settings obj
    settings = scan_settings.ScanSettings(
        int(arg_dict['motor_speed']),   # desired motor speed setting
        int(arg_dict['sample_rate']),   # desired sample rate setting
        int(arg_dict['dead_zone']),     # starting angle of deadzone
        int(arg_dict['angular_range']),  # angular range of scan
        # mount angle of device relative to horizontal
        int(arg_dict['mount_angle'])
    )

    # Create an exporter
    exporter = scan_exporter.ScanExporter(file_name=arg_dict['output'])

    # Create a scanner object
    scanner = Scanner(settings=settings, exporter=exporter)

    # Setup the scanner
    scanner.setup()

    # Perform the scan
    scanner.perform_scan()

    # Stop the scanner
    scanner.idle()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Creates a 3D scanner and performs a scan')
    parser.add_argument('-ms', '--motor_speed',
                        help='Motor Speed (integer from 1:10)',
                        default=sweep_constants.MOTOR_SPEED_1_HZ,
                        required=False)
    parser.add_argument('-sr', '--sample_rate',
                        help='Sample Rate(either 500, 750 or 1000)',
                        default=sweep_constants.SAMPLE_RATE_500_HZ,
                        required=False)
    parser.add_argument('-ar', '--angular_range',
                        help='Angular range of scan (integer from 1:180)',
                        default=180,
                        required=False)
    parser.add_argument('-ma', '--mount_angle',
                        help='Mount angle of device relative to horizontal',
                        default=-90,
                        required=False)
    parser.add_argument('-dz', '--dead_zone',
                        help='Starting angle of deadzone',
                        default=135,
                        required=False)
    default_filename = "Scan " + datetime.datetime.fromtimestamp(
        time.time()).strftime('%Y-%m-%d %H-%M-%S') + '.csv'
    parser.add_argument('-o', '--output',
                        help='Filepath for the exported scan',
                        default=default_filename,
                        required=False)

    args = parser.parse_args()
    argsdict = vars(args)

    main(argsdict)
