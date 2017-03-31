"""Defines the intermediate app that controls the scanner from the webapp"""
import atexit
import scanner_communication
import time

from sweeppy import Sweep
import scanner
import scan_settings
import scan_exporter
import threading
import sys


class ScannerApp(object):
    """The app that controls the scanner based on communication with the webapp.
    Attributes:
        scanner: the 3D scanner
        communicator: communicates with the webapp
    """

    def __init__(self):
        """Return a ScannerApp object
        """
        self.scanner = None

        # create a communicator
        self.communicator = scanner_communication.Communicator(
            parent_app=self, address="localhost", sub_port=3000, pub_port=5000)

        atexit.register(self.shutdown)

        self.loop()

    def loop(self):
        """Logic loop"""
        while True:
            command = self.communicator.wait_for_command()
            self.handle_command(command)

    def handle_command(self, command):
        """Handles command"""
        if command['cmd_type'] == "perform_scan":
            self.perform_scan(command['data'])
        else:
            print "Command type [{}] is not recognized.".format(command['cmd_type'])

    def perform_scan(self, scan_params):
        """Performs a scan with the scan parameters, while sending updates over communicator"""
        # create a settings object
        settings = scan_settings.ScanSettings(
            int(scan_params.motor_speed),   # desired motor speed setting
            int(scan_params.sample_rate),   # desired sample rate setting
            120,                            # starting angle of deadzone
            int(scan_params.angular_range),  # angular range of scan
            -90                 # mount angle of device relative to horizontal
        )

        # Create an exporter
        print '{}.csv'.format(scan_params.file_name)
        exporter = scan_exporter.ScanExporter(
            file_name='{}.csv'.format(scan_params.file_name)
        )

        failure_msg = None
        try:
            with Sweep('/dev/ttyUSB0') as sweep:
                try:
                    print "Creating Scanner..."
                    # Create a scanner object
                    self.scanner = scanner.Scanner(
                        device=sweep, settings=settings, exporter=exporter)
                except:
                    failure_msg = "Failed to create scanner"
                    self.scanner = None
                    raise

                # setup the base in a dedicated thread
                thr = threading.Thread(
                    target=self.repeat_status_reports, args=(), kwargs={})
                thr.start()

                # Setup the scanner
                try:
                    print "Running setup..."
                    self.scanner.setup()
                except:
                    failure_msg = "Failed to setup scanner"
                    self.scanner = None
                    thr.join()
                    raise

                # Perform the scan
                try:
                    print "Performing scan..."
                    self.scanner.perform_scan()
                except:
                    failure_msg = "Failed to perform scan"
                    self.scanner = None
                    thr.join()
                    raise

                # Stop the scanner
                try:
                    print "Setting the scanner to idle..."
                    self.scanner.idle()
                except:
                    failure_msg = "Failed to set device to idle"
                    self.scanner = None
                    thr.join()
                    raise

                # Ensure the "complete" status is sent as an update
                self.report_scanner_status()
                self.scanner = None

                # Wait for the base setup to complete, then join and return
                thr.join()

        except KeyboardInterrupt:
            print 'User terminated the program.'
            print 'Please disconnect and reconnect sensor before running the script again.'
            self.scanner = None
            failure_msg = "User terminated the program. Please disconnect and reconnect sensor before trying again."
            self.report_failure(msg=failure_msg)
        except:
            print 'Error: {}'.format(sys.exc_info()[0])
            print 'An error terminated the program.'
            print 'Please disconnect and reconnect sensor before running the script again.'
            self.scanner = None
            self.report_failure(msg=failure_msg)

    def report_failure(self, msg):
        """Reports failure as a scanner update"""
        if self.scanner is not None:
            self.scanner.set_status(status="failed", msg=msg)

        data = {}
        data['status'] = "failure"
        data['msg'] = msg

        self.communicator.send_update(data)

    def repeat_status_reports(self, duration=None):
        """Sends status reports every "duration" seconds"""
        if duration is None:
            duration = 1.5
        while self.scanner is not None:
            self.report_scanner_status()
            time.sleep(duration)

    def report_scanner_status(self):
        """Reports the current status of the scanner"""
        if self.scanner is not None:
            status = self.scanner.get_status()
            if status is not None:
                self.communicator.send_update(status)

    def shutdown(self):
        """Shuts down the app. Useful on exit"""


def main():
    """Manages a scanner controlled by the webapp."""
    print "Running Python application..."
    app = ScannerApp()

    print "Done!"

if __name__ == '__main__':
    main()
