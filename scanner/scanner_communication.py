"""Communicates info back and forth from the webapp"""
import atexit
import sys
import time
import zmq
import json


class MsgPerformScan(object):
    """Message type defining scan parameters for performing a scan"""

    def __init__(self, jsonString):
        self.__dict__ = json.loads(jsonString)


class Communicator(object):
    """Handles communication via messages.
    Attributes:
        context: the zmq context
        cmd_subscriber: socket that subscribes to command messages
        parent_app: the application that created this communicator
    """

    def __init__(self, parent_app=None, address=None, sub_port=None, pub_port=None):
        """Return a ScannerApp object
        """
        if address is None:
            address = "localhost"
        if sub_port is None:
            sub_port = 3000
        if pub_port is None:
            pub_port = 5000
        if parent_app is None:
            parent_app = self

        self.parent_app = parent_app

        # create a zmq context
        self.context = zmq.Context()

        # Connect a subscriber socket to listen for commands
        self.cmd_subscriber = self.context.socket(zmq.SUB)
        self.cmd_subscriber.connect('tcp://{}:{}'.format(address, sub_port))
        self.cmd_subscriber.setsockopt(zmq.SUBSCRIBE, "cmd_msg")

        # Bind a publisher socket to publish status updates
        # ...
        self.update_publisher = self.context.socket(zmq.PUB)
        self.update_publisher.bind('tcp://*:{}'.format(pub_port))

        time.sleep(1)

        # self.wait_for_command()

        atexit.register(self.shutdown)

    def wait_for_command(self):
        """Listens for incoming command messages and responds appropriately"""
        # Process commands
        poller = zmq.Poller()
        poller.register(self.cmd_subscriber, zmq.POLLIN)

#        while True:
        # Wait until a socket receives a message
        try:
            socks = dict(poller.poll())
        except KeyboardInterrupt:
            return

        # Check to see which socket received the message and handle it
        if self.cmd_subscriber in socks:
            parts = self.cmd_subscriber.recv_multipart()
            topic = parts[0]
            cmd_type = parts[1]
            msg = parts[2]
            data = self.process_msg(cmd_type, msg)
            return {'topic': topic, 'cmd_type': cmd_type, 'data': data}

    def process_msg(self, cmd_type, msg):
        """Process a received command"""
        if cmd_type == "perform_scan":
            return MsgPerformScan(msg)
        else:
            print "{} is not a recognized command type.".format(cmd_type)
            return None

    def handle_command(self, cmd_type, data):
        """Prints the command and data"""
        if cmd_type == "perform_scan":
            print "{} {} {} {}".format(
                data.motor_speed,
                data.sample_rate,
                data.angular_range,
                data.file_name
            )
        else:
            print "{} is not a recognized command type.".format(cmd_type)

    def send_update(self, data):
        """Sends an update"""
        json_data = json.dumps(data)
        print json_data
        self.update_publisher.send_multipart(["scan_update", json_data])

    def shutdown(self):
        """Shuts down the app. Useful on exit"""


def main():
    """Handles communication via messages."""
    print "No main test for this module."

if __name__ == '__main__':
    main()
