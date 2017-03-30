"""Defines the intermediate app that controls the scanner from the webapp"""
import atexit
import scanner_communication
import scanner

class ScannerApp(object):
    """The app that controls the scanner based on communication with the webapp.
    Attributes:
        communicator: communicates with the webapp
    """

    def __init__(self):
        """Return a ScannerApp object
        """
        # create a communicator
        self.communicator = scanner_communication.Communicator(
            parent_app=self, address="localhost", port=3000)

        self.communicator.wait_for_command()

        atexit.register(self.shutdown)

    def handle_command(self, cmd_type, data):
        """Handles command"""
        if cmd_type == "perform_scan":
            scanner.perform_scan(data)
        else:
            print "{} is not a recognized command type.".format(cmd_type)

    def shutdown(self):
        """Shuts down the app. Useful on exit"""


def main():
    """Manages a scanner controlled by the webapp."""
    print "Running Python application..."
    app = ScannerApp()


    print "Done!"

if __name__ == '__main__':
    main()
