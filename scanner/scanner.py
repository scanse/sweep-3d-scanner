"""Defines a 3D scanner"""
import argparse
import time
import datetime
import math
import threading
import sweep_helpers
import scan_settings
import scan_exporter
import scan_utils
import scanner_base
from scanner_output import output_json_message


class Scanner(object):
    """The 3d scanner.
    Attributes:
        base: the rotating base
        device: the sweep scanning LiDAR
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
        if device is None:
            self.shutdown()
        if base is None:
            self.shutdown()
        if settings is None:
            settings = scan_settings.ScanSettings()
        if exporter is None:
            exporter = scan_exporter.ScanExporter()

        self.base = base
        self.device = device
        self.settings = settings
        self.exporter = exporter
        self.received_scan = False

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
        self.device.reset()

        # sleep for at least the minimum time required to reset the device
        time.sleep(reset_max_duration)

        output_json_message(
            {'type': "update", 'status': "setup", 'msg': "Adjusting device settings."})

        # Set the sample rate
        self.device.set_sample_rate(self.settings.get_sample_rate())

        # Set the motor speed
        self.device.set_motor_speed(self.settings.get_motor_speed())

    def setup(self):
        """Setup the scanner according to the scan settings"""
        # setup the device, wait for it to calibrate
        self.setup_device()

        # wait until the device is ready, so as not to disrupt the calibration
        while True:
            if self.device.get_motor_ready() is True:
                break

            # Convey that the motor speed is still adjusting
            output_json_message({'type': "update", 'status': "setup",
                                 'msg': "Waiting for calibration routine and motor speed to stabilize."})

            time.sleep(0.5)

        # setup the base
        self.setup_base()

    def perform_scan(self):
        """Performs a 3d scan"""
        # Calcualte some intermediate values
        num_sweeps, angle_between_sweeps, steps_per_move = self.calculate_scan_variables()

        # Report that the scan is initiating, and start scanning
        self.report_scan_initiated(num_sweeps)
        self.device.start_scanning()

        # put a 3 second timeout on the get_scans() method in case it hangs
        time_out_thread = threading.Timer(3, self.check_get_scan_timeout)
        time_out_thread.start()

        valid_scan_index = 0
        rotated_already = False

        # get_scans is coroutine-based generator returning scans ad infinitum
        for scan_count, scan in enumerate(self.device.get_scans()):
            # note the arrival time
            scan_arrival_time = time.time()

            # note that a scan was received (used to avoid the timeout)
            self.received_scan = True

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

            # Catch scans that contain unordered samples and discard them
            # (this may indicate problem reading sync byte)
            if scan_utils.contains_unordered_samples(scan):
                continue

            # Edge case (discard 1st scan without base movement and move base)
            if not rotated_already:
                # Wait for the device to reach the threshold angle for movement
                self.wait_until_deadzone(scan_arrival_time)

                # Move the base and start again
                self.base.move_steps(steps_per_move)
                rotated_already = True
                continue

            # Export the scan
            self.exporter.export_2D_scan(
                scan, valid_scan_index, angle_between_sweeps,
                self.settings.get_mount_angle(), False)

            # increment the scan index
            valid_scan_index = valid_scan_index + 1

            # Wait for the device to reach the threshold angle for movement
            self.wait_until_deadzone(scan_arrival_time)

            # Move the base and report progress
            self.base.move_steps(steps_per_move)
            self.report_scan_progress(num_sweeps, valid_scan_index)

            # Exit after collecting the required number of 2D scans
            if valid_scan_index >= num_sweeps:
                break

        # Stop scanning and report completion
        self.device.stop_scanning()
        self.report_scan_complete()

    def idle(self):
        """Stops the device from spinning"""
        self.device.set_motor_speed(sweep_helpers.MOTOR_SPEED_0_HZ)

    def calculate_scan_variables(self):
        """ Calculates and returns intermediate variables necessary to perform a scan """
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

        # Correct the num_sweeps...
        # Account for the accumulated difference due to rounding
        num_sweeps = math.floor(
            1.0 * self.settings.get_scan_range() / angle_between_sweeps)
        # Account for gap introduced from splitting each scan
        num_sweeps = num_sweeps + 2

        return (num_sweeps, angle_between_sweeps, num_stepper_steps_per_move)

    def check_get_scan_timeout(self):
        """Checks if we have received a scan from getScan... if not, exit"""
        if not self.received_scan:
            self.base.turn_off_motors()
            raise ValueError("getScan() never returned... aborting")
            # Should work out a better solution to shutdown.
            # Signaling with KeyboardInterrupt doesn't seem to work and process still hangs
            # Currently the workaround is that the node app will kill this
            # process if it receives an error

    def wait_until_deadzone(self, t_0):
        """ Waits the however long is required to reach the deadzone
        :param t_0: The time the sweep crossed the 0 degree mark
        """
        time_until_deadzone = self.settings.get_time_to_deadzone_sec() - \
            (time.time() - t_0)
        if time_until_deadzone > 0:
            time.sleep(time_until_deadzone)

    def report_scan_initiated(self, num_sweeps):
        """ Reports that a scan has been initiated """
        output_json_message({
            'type': "update",
            'status': "scan",
            'msg': "Initiating scan...",
            'duration': num_sweeps / self.settings.get_motor_speed(),
            'remaining': num_sweeps / self.settings.get_motor_speed()
        })

    def report_scan_progress(self, num_sweeps, valid_scan_index):
        """ Reports the progress of a scan """
        output_json_message({
            'type': "update",
            'status': "scan",
            'msg': "Scan in Progress...",
            'duration': num_sweeps / self.settings.get_motor_speed(),
            'remaining': (num_sweeps - valid_scan_index) / self.settings.get_motor_speed()
        })

    def report_scan_complete(self):
        """ Reports the completion of a scan """
        output_json_message({
            'type': "update",
            'status': "complete",
            'msg': "Finished scan!"
        })

    def shutdown(self):
        """Print message and shutdown"""
        exit()


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

    use_dummy = arg_dict['use_dummy']

    # Create a scanner base
    base = scanner_base.ScannerBase(use_dummy=use_dummy)

    # Create sweep sensor, and perform scan
    with sweep_helpers.create_sweep_w_error('/dev/ttyUSB0', use_dummy) as (sweep, err):
        if err:
            output_json_message(
                {'type': "update", 'status': "failed", 'msg': "Failed to connect to sweep device... make sure it is plugged in."})
            time.sleep(0.1)
            return
        # Create a scanner object
        time.sleep(1.0)
        scanner = Scanner(
            device=sweep, base=base, settings=settings, exporter=exporter)

        # Setup the scanner
        scanner.setup()

        # Perform the scan
        scanner.perform_scan()

        # Stop the scanner
        time.sleep(1.0)
        scanner.idle()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Creates a 3D scanner and performs a scan')
    parser.add_argument('-ms', '--motor_speed',
                        help='Motor Speed (integer from 1:10)',
                        default=sweep_helpers.MOTOR_SPEED_1_HZ,
                        required=False)
    parser.add_argument('-sr', '--sample_rate',
                        help='Sample Rate(either 500, 750 or 1000)',
                        default=sweep_helpers.SAMPLE_RATE_500_HZ,
                        required=False)
    parser.add_argument('-ar', '--angular_range',
                        help='Angular range of scan (integer from 1:180)',
                        default=180,
                        required=False)
    parser.add_argument('-ma', '--mount_angle',
                        help='Mount angle of device relative to horizontal',
                        default=90,
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
    parser.add_argument('-d', '--use_dummy',
                        help='Use the dummy verison without hardware',
                        default=False,
                        action='store_true',
                        required=False)

    args = parser.parse_args()
    argsdict = vars(args)

    main(argsdict)
