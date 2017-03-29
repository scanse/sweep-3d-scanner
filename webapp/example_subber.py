import sys
import time
import zmq
import json


def main():
    print 'Running test'

    class Receipt(object):

        def __init__(self, jsonString):
            self.__dict__ = json.loads(jsonString)

    context = zmq.Context()

    # First, connect our subscriber socket
    cmd_subscriber = context.socket(zmq.SUB)
    cmd_subscriber.connect('tcp://localhost:3000')
    cmd_subscriber.setsockopt(zmq.SUBSCRIBE, "perform_scan")

    time.sleep(1)

    total_value = 0
    while True:
        parts = cmd_subscriber.recv_multipart()
        topic = parts[0]
        msg = parts[1]

        scan_params = Receipt(msg)
        print "{} {} {} {}".format(
            scan_params.motor_speed,
            scan_params.sample_rate,
            scan_params.angular_range,
            scan_params.file_name
        )

if __name__ == '__main__':
    main()
