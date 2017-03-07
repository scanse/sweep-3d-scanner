"""Defines a 3D scanner"""
from sweeppy import Sweep
import sweep_constants
import scan_settings
import scanner_base
import scan_exporter
import scan_utils
import time
import math


class Scanner(object):
    """The 3d scanner.
    Attributes:
        base: the rotating base
        device: the sweep scanning LiDAR
        settings: the scan settings
        exporter: the scan exporter
    """

    def __init__(self, base=None, device=None, settings=None, exporter=None):
        """Return a Scanner object
        :param base:  the scanner base
        :param device: the sweep device
        :param settings: the scan settings
        :param exporter: the scan exporter
        """
        if base is None:
            base = scanner_base.ScannerBase()
        if device is None:
            device = Sweep()
        if settings is None:
            settings = scan_settings.ScanSettings()
        if exporter is None:
            exporter = scan_exporter.ScanExporter()

        self.base = base
        self.device = device
        self.settings = settings
        self.exporter = exporter

    def setup(self):
        """Setups up the device according to the scan settings"""
        self.device.reset()
        # sleep for 5 seconds, allowing time for device to reset
        time.sleep(5)

        # Set the motor speed and sample rate
        self.device.set_motor_speed(self.settings.get_motor_speed())
        self.device.set_sample_rate(self.settings.get_sample_rate())

        print 'Motor Speed: {} Hz'.format(self.device.get_motor_speed())
        print 'Sample Rate: {} Hz'.format(self.device.get_sample_rate())

        # sleep for 4 seconds, allowing time for motor speed to adjust
        time.sleep(4)

    def idle(self):
        """Stops the device from spinning"""
        self.device.set_motor_speed(sweep_constants.MOTOR_SPEED_0_HZ)

    def perform_scan(self):
        """Performs a complete 3d scan
        :param angular_range: the angular range for the base to cover during the scan (default 180)
        """
        print "Performing 3D scan"
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

        # Start Scanning
        self.device.start_scanning()

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
            self.exporter.export_2D_scan(scan, scan_count, self.settings.get_mount_angle(
            ), angle_between_sweeps * scan_count)

            # Wait for the device to reach the threshold angle for movement
            time.sleep(self.settings.get_time_to_deadzone_sec())

            # Move the base
            self.base.move_steps(num_stepper_steps_per_move)

            # Collect the appropriate number of 2D scans
            if scan_count == num_sweeps:
                break
        self.device.stop_scanning()

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


def main():
    """Creates a 3D scanner and gather 90 degrees worth of scan"""
    with Sweep() as sweep:
        # Create a scan settings obj
        settings = scan_settings.ScanSettings(
            sweep_constants.MOTOR_SPEED_1_HZ,       # desired motor speed setting
            sweep_constants.SAMPLE_RATE_500_HZ,     # desired sample rate setting
            120,                                    # starting angle of deadzone
            180,                                    # angular range of scan
            -90)                                    # mount angle of device relative to horizontal
        # Create a default base obj
        base = scanner_base.ScannerBase()
        # Create a scanner object
        scanner = Scanner(base, sweep, settings)

        # Setup the scanner
        scanner.setup()

        # Perform the scan
        scanner.perform_scan()

        # Stop the scanner
        scanner.idle()

if __name__ == '__main__':
    main()
