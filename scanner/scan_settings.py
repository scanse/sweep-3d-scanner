"""Holds parameters and settings for 3D the scanner."""
import sweep_helpers


class ScanSettings(object):
    """A set of scan settings
    Attributes:
        motor_speed:    Sweep device motor speed in HZ
        sample_rate:    Sweep device sample rate in HZ
        deadzone:       Angle at which the base should begin rotating
                        (measured in degrees from sweep device 0 angle)
        scan_range:     Angular range (in degrees) for the scan to cover
        mount_angle:    Mount angle of the device relative to horizontal plane
    """

    def __init__(self, motor_speed=None, sample_rate=None, deadzone=None,
                 scan_range=None, mount_angle=None):
        """Return a ScanSettings object.
        :param motorSpeed:  Integer value between 1:10 representing motor speed in HZ
        :param sampleRate:  Integer value (500, 750 or 1000), representing a sample rate in HZ
        :param deadzone:    Integer value between 0:180, angle at which the base should begin
                            rotating (measured in degrees from sweep device 0 angle)
        :param scan_range:  Range of movement for the scan to cover (default 180deg)
        :param mount_angle: Mount angle of the device relative to horizontal plane (defaults 90deg)
        """
        if motor_speed is None:
            motor_speed = sweep_helpers.MOTOR_SPEED_1_HZ
        if sample_rate is None:
            sample_rate = sweep_helpers.SAMPLE_RATE_500_HZ
        if deadzone is None:
            deadzone = 135
        if scan_range is None:
            scan_range = 180
        if mount_angle is None:
            mount_angle = 90
        self.motor_speed = motor_speed
        self.sample_rate = sample_rate
        self.deadzone = deadzone
        self.scan_range = scan_range
        self.mount_angle = mount_angle
        self.min_range_val = 10
        self.max_range_val = 4000

    def set_motor_speed(self, motor_speed=None):
        """Sets the motor speed setting
        :param motor_speed: an integer value between 1:10 representing motor speed in HZ
        """
        if motor_speed is None:
            motor_speed = sweep_helpers.MOTOR_SPEED_1_HZ
        self.motor_speed = motor_speed

    def set_sample_rate(self, sample_rate=None):
        """Sets the sample rate setting
        :param sample_rate: an integer value (500, 750 or 1000), representing a sample rate in HZ
        """
        if sample_rate is None:
            sample_rate = sweep_helpers.SAMPLE_RATE_500_HZ
        self.sample_rate = sample_rate

    def set_deadzone(self, deadzone=None):
        """Sets the threshold angle setting
        :param deadzone: an integer value between 0:180, representing the angle (in degrees)
                            at which the base should begin rotating (ie: start of the deadzone)
        """
        if deadzone is None:
            deadzone = 145
        self.deadzone = deadzone

    def set_scan_range(self, scan_range=None):
        """Sets the movement range for the scan.
        :param scan_range:  Range of movement for the scan to cover (default 180deg)
        """
        if scan_range is None:
            scan_range = 180
        self.scan_range = scan_range

    def set_mount_angle(self, mount_angle=None):
        """Sets the mount angle of the device
        :param mount_angle: Mount angle of device relative to horizontal plane (default 90deg)
        """
        if mount_angle is None:
            mount_angle = 90
        self.mount_angle = mount_angle

    def get_motor_speed(self):
        """Returns the motor speed setting in HZ"""
        return self.motor_speed

    def get_sample_rate(self):
        """Returns the sample rate setting in HZ"""
        return self.sample_rate

    def get_min_range_val(self):
        """Returns the minimum range value for a sensor reading to be recorded"""
        return self.min_range_val

    def get_max_range_val(self):
        """Returns the maximum range value for a sensor reading to be recorded"""
        return self.max_range_val

    def get_deadzone(self):
        """Returns the threshold angle setting"""
        return self.deadzone

    def get_scan_range(self):
        """Returns the range of movement (in degrees) for the scan"""
        return self.scan_range

    def get_mount_angle(self):
        """Returns the mount angle of the device relative to horizontal plane (in deg)"""
        return self.mount_angle

    def get_resolution(self):
        """Returns the resolution which results from the settings in samples/deg"""
        return 1.0 * self.sample_rate / (self.motor_speed * 360)

    def get_step_size_deg(self):
        """Returns the ideal base step size (in degrees) required to match the
        horizontal & vertical resolutions
        """
        return 1.0 / self.get_resolution()

    def get_time_to_deadzone_ms(self):
        """Returns the time required for sensor to travel between 0 deg and deadzone (in ms)"""
        return int(round(1000 * self.deadzone / (360 * self.motor_speed)))

    def get_time_to_deadzone_sec(self):
        """Returns the time required for sensor to travel between 0 deg and deadzone (in sec)"""
        return self.deadzone / (360.0 * self.motor_speed)

    def print_details(self):
        """Prints info about this scan parameters object"""
        print "ScanSettings Object"
        print "\tMotor speed: {} HZ".format(self.get_motor_speed())
        print "\tSample rate: {} HZ".format(self.get_sample_rate())
        print "\tDeadzone angle: {} degrees".format(self.get_deadzone())
        print "\tTime to reach deadzone angle: {} ms, or {} sec".format(
            self.get_time_to_deadzone_ms(), self.get_time_to_deadzone_sec())
        print "\tResolution: {} samples/degree".format(self.get_resolution())
        print "\tStep size: {} degrees".format(self.get_step_size_deg())


def main():
    """Creates two ScanSettings objects (1 default, 1 custom) and prints their details."""
    # Create a ScanSettings obj with default settings
    default_params = ScanSettings()
    # Create a ScanSettings obj with specific settings
    custom_params = ScanSettings(
        sweep_helpers.MOTOR_SPEED_2_HZ,       # desired motor speed setting
        sweep_helpers.SAMPLE_RATE_750_HZ,     # desired sample rate setting
        135,                                    # desired deadzone angle threshold
        180,                                    # desired range of movement
        90)                                    # mount angle of device relative to horizontal plane

    # Prints details for both objects
    default_params.print_details()
    custom_params.print_details()

if __name__ == '__main__':
    main()
