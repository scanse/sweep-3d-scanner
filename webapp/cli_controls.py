import subprocess
import sys
import os


def idle():
    """ Sets the device to idle"""
    curr_pathname = os.path.dirname(sys.argv[0])
    curr_abs_pathname = os.path.abspath(curr_pathname)
    abs_script_path = os.path.join(curr_abs_pathname, 'scanner/idle.py')
    command = "python {}".format(abs_script_path)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output


def shutdown_pi():
    """ Shuts down the raspberry pi"""
    command = "/usr/bin/sudo halt"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output


def restart_pi():
    """Restarts the raspberry pi"""
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output


def test_base():
    """Performs a test on the scanner base"""
    curr_pathname = os.path.dirname(sys.argv[0])
    curr_abs_pathname = os.path.abspath(curr_pathname)
    abs_script_path = os.path.join(curr_abs_pathname, 'scanner/scanner_base.py')
    command = "python {}".format(abs_script_path)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output


def test_limit_switch():
    """Performs a test on the limit switch"""
    curr_pathname = os.path.dirname(sys.argv[0])
    curr_abs_pathname = os.path.abspath(curr_pathname)
    abs_script_path = os.path.join(curr_abs_pathname, 'scanner/scanner_limit_switch.py')
    command = "python {}".format(abs_script_path)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output


def perform_scan(motor_speed=None, sample_rate=None, angular_range=None, output_path=None):
    """Performs a scan"""
    curr_pathname = os.path.dirname(sys.argv[0])
    curr_abs_pathname = os.path.abspath(curr_pathname)
    abs_script_path = os.path.join(curr_abs_pathname, 'scanner/scanner.py')
    command = 'python {} --motor_speed={} --sample_rate={} --angular_range={} --output={}'.format(
        abs_script_path,
        motor_speed,
        sample_rate,
        int(round(angular_range / 2)),
        output_path
    )
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output
