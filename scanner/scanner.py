"""Defines a 3D scanner"""
from sweeppy import Sweep
import sweep_constants
import scan_settings
import scanner_base
import scan_exporter
import scan_utils
import time
import datetime
import math
import atexit
import threading
import sys
import argparse
import json


class Scanner(object):
    """The 3d scanner.
    Attributes:
        base: the rotating base
        device: the sweep scanning LiDAR
        settings: the scan settings
        exporter: the scan exporter
    """

    # , updates=None):
    def __init__(self, device=None, base=None, settings=None, exporter=None):
        """Return a Scanner object
        :param base:  the scanner base
        :param device: the sweep device
        :param settings: the scan settings
        :param exporter: the scan exporter
        :param updates: an optional communicator object that communicates updates
        """
        if device is None:
            self.shutdown("Please provide a device to scanner constructor.")
        if base is None:
            base = scanner_base.ScannerBase()
        if settings is None:
            settings = scan_settings.ScanSettings()
        if exporter is None:
            exporter = scan_exporter.ScanExporter()

        self.base = base
        self.device = device
        self.settings = settings
        self.exporter = exporter
        self.status_lock = threading.Lock()
        self.status = None

    def setup_base(self):
        """Setup the base"""
        self.base.reset()

    def setup_device(self):
        """Setup the device"""
        print "Setup Device..."

        reset_min_duration = 7.0
        time_between_commands = 0.5

        self.set_status(status="setup", msg="Resetting device.",
                        duration=reset_min_duration)

        # Reset the device
        self.device.reset()

        # sleep for at least the minimum time required to reset the device
        print 'Resetting device, waiting {} seconds'.format(reset_min_duration)
        time.sleep(reset_min_duration)

        # Set the motor speed
        time.sleep(time_between_commands)
        adjust_start_time = time.time()

        self.set_status(
            status="setup", msg="Adjusting device settings.", duration=2.0)
        # if self.updates is not None:
        #     self.updates.send_update(
        #         status="setup",
        #         msg="Adjusting device settings.",
        #         duration=2.0
        #     )
        self.device.set_motor_speed(self.settings.get_motor_speed())

        # Set the sample rate
        time.sleep(time_between_commands)
        self.device.set_sample_rate(self.settings.get_sample_rate())

        # Confirm motor speed
        time.sleep(time_between_commands)
        print '\tMotor Speed: {} Hz'.format(self.device.get_motor_speed())

        # Confirm sample rate
        time.sleep(time_between_commands)
        print '\tSample Rate: {} Hz'.format(self.device.get_sample_rate())

        # Allow at least 4 seconds for motor speed to adjust
        sleep_duration = 4.0 - adjust_start_time
        if sleep_duration > 0:
            self.set_status(
                status="setup", msg="Waiting for motor speed to stabilize.", duration=sleep_duration)
            time.sleep(sleep_duration)

    def setup(self):
        """Setup the scanner according to the scan settings"""
        # setup the device and base concurrently

        # setup the base in a dedicated thread
        thr = threading.Thread(target=self.setup_base, args=(), kwargs={})
        thr.start()

        # setup the device in the main thread
        self.setup_device()

        # Wait for the base setup to complete, then join and return
        thr.join()

    def idle(self):
        """Stops the device from spinning"""
        self.device.set_motor_speed(sweep_constants.MOTOR_SPEED_0_HZ)

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

        self.set_status(status="scan", msg="Initiating scan...", duration=num_sweeps /
                        self.settings.get_motor_speed(), remaining=num_sweeps / self.settings.get_motor_speed())

        # Start Scanning
        self.device.start_scanning()

        print "Successfully started scanning..."
        # get_scans is coroutine-based generator lazily returning scans ad
        # infinitum
        for scan_count, scan in enumerate(self.device.get_scans()):
            # remove readings from unreliable distances
            scan_utils.remove_distance_extremes(
                scan, self.settings.get_min_range_val(), self.settings.get_max_range_val())

            # Remove readings from the deadzone
            scan_utils.remove_angular_window(
                scan, self.settings.get_deadzone(), 360 - self.settings.get_deadzone())

            if len(scan.samples) > self.settings.get_max_samples_per_scan():
                continue

            # Export the scan
            self.exporter.export_2D_scan(
                scan,
                scan_count,
                self.settings.get_mount_angle(),
                angle_between_sweeps * scan_count,
                False
            )

            # Wait for the device to reach the threshold angle for movement
            time.sleep(self.settings.get_time_to_deadzone_sec())

            # Move the base
            self.base.move_steps(num_stepper_steps_per_move)

            self.set_status(status="scan", msg="Scan in Progress...", duration=num_sweeps /
                            self.settings.get_motor_speed(), remaining=(num_sweeps - scan_count) / self.settings.get_motor_speed())

            # Collect the appropriate number of 2D scans
            if scan_count == num_sweeps:
                break
        # Stop scanning
        self.device.stop_scanning()

        self.set_status(status="complete", msg="Finished scan!")

    def set_status(self, status, msg, duration=None, remaining=None):
        """Sets the status of the scanner"""
        data = {}
        data['status'] = status
        data['msg'] = msg
        if duration is not None:
            data['duration'] = duration
        if remaining is not None:
            data['remaining'] = remaining

        with self.status_lock:
            self.status = data

    def get_status(self):
        """Returns the status of the scanner"""
        with self.status_lock:
            return self.status

    def shutdown(self, msg=None):
        """Print message and shutdown"""
        if msg is not None:
            print '{}'.format(msg)

        print 'Shutting down.'
        exit()

    def get_base(self):
        """Returns the ScannerBase object for this scanner"""
        return self.base

    def set_base(self, base=None):
        """Sets the base for this scanner to the provided ScannerBase object"""
        if base is None:
            base = scanner_base.ScannerBase()
        self.base = base

    def get_device(self):
        """Returns the Sweep device for this scanner"""
        return self.device

    def set_device(self, device=None):
        """Sets the Sweep device for this scanner to the provided Sweep"""
        if device is None:
            device = Sweep()
        self.device = device

    def get_settings(self):
        """Returns the scan settings for this scanner"""
        return self.settings

    def set_settings(self, settings=None):
        """Sets the scan settings for this scanner to the provided ScanSettings object"""
        if settings is None:
            settings = scan_settings.ScanSettings()
        self.settings = settings


def main(arg_dict):
    """Creates a 3D scanner and gather a scan"""
    print "Main..."
    # Create a scan settings obj
    settings = scan_settings.ScanSettings(
        # desired motor speed setting
        int(arg_dict['motor_speed']),
        # desired sample rate setting
        int(arg_dict['sample_rate']),
        # starting angle of deadzone
        int(arg_dict['dead_zone']),
        int(arg_dict['angular_range']),     # angular range of scan
        # mount angle of device relative to horizontal
        int(arg_dict['mount_angle'])
    )
    # settings = scan_settings.ScanSettings(
    #     sweep_constants.MOTOR_SPEED_1_HZ,       # desired motor speed setting
    #     sweep_constants.SAMPLE_RATE_500_HZ,     # desired sample rate setting
    #     120,                            # starting angle of deadzone
    #     180,                            # angular range of scan
    #     -90)                            # mount angle of device relative to horizontal

    # Create an exporter
    exporter = scan_exporter.ScanExporter(
        file_name=arg_dict['output']
    )
    try:
        print "trying..."
        with Sweep('/dev/ttyUSB0') as sweep:
            print "Creating Scanner..."
            # Create a scanner object
            scanner = Scanner(
                device=sweep, settings=settings, exporter=exporter)

            # Setup the scanner
            print "Running setup..."
            scanner.setup()

            # Perform the scan
            print "Performing scan..."
            scanner.perform_scan()

            # Stop the scanner
            print "Setting the scanner to idle..."
            scanner.idle()
    except KeyboardInterrupt:
        print 'User terminated the program.'
        print 'Please disconnect and reconnect sensor before running the script again.'
        exit()
    except:
        print 'Error: {}'.format(sys.exc_info()[0])
        print 'An error terminated the program.'
        print 'Please disconnect and reconnect sensor before running the script again.'
        exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Creates a 3D scanner and performs a scan')
    parser.add_argument('-ms', '--motor_speed',
                        help='Motor Speed (integer from 1:10)',
                        default=sweep_constants.MOTOR_SPEED_1_HZ, required=False)
    parser.add_argument('-sr', '--sample_rate',
                        help='Sample Rate(either 500, 750 or 1000)',
                        default=sweep_constants.SAMPLE_RATE_500_HZ, required=False)
    parser.add_argument('-ar', '--angular_range',
                        help='Angular range of scan (integer from 1:180)',
                        default=180, required=False)
    parser.add_argument('-ma', '--mount_angle',
                        help='Mount angle of device relative to horizontal',
                        default=-90, required=False)
    parser.add_argument('-dz', '--dead_zone',
                        help='Starting angle of deadzone',
                        default=120, required=False)
    default_filename = "Scan " + datetime.datetime.fromtimestamp(
        time.time()).strftime('%Y-%m-%d %H-%M-%S') + '.csv'
    parser.add_argument('-o', '--output',
                        help='Filepath for the exported scan',
                        default=default_filename, required=False)

    args = parser.parse_args()
    argsdict = vars(args)

    main(argsdict)
