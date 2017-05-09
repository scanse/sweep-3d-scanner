"""Tests the sweep's basic functions"""
import time
import sys
import json


def main():
    """Tests the sweep's basic functions"""
    output_json_message(
        {'type': "update", 'status': "setup", 'msg': "Testing motor ready."})

    output_json_message(
        {'type': "update", 'status': "setup", 'msg': "Adjusting sample rate."})

    time.sleep(0.1)

    output_json_message(
        {'type': "update", 'status': "setup", 'msg': "Adjusting motor speed."})

    time.sleep(5.0)

    output_json_message(
        {'type': "update", 'status': "setup", 'msg': "Testing motor ready."})

    output_json_message(
        {'type': "update", 'status': "setup", 'msg': "Starting data acquisition."})

    time.sleep(7.0)

    output_json_message(
        {'type': "update", 'status': "setup", 'msg': "Stopping data acquisition."})

    time.sleep(0.1)

    output_json_message(
        {'type': "update", 'status': "success", 'msg': "Done."})


def output_message(message):
    """Print the provided input & flush stdout so parent process registers the message"""
    print message
    sys.stdout.flush()


def output_json_message(json_input):
    """Print the provided json & flush stdout so parent process registers the message"""
    serialized_json = json.dumps(json_input, separators=(',', ':'))
    output_message(serialized_json)

if __name__ == '__main__':
    main()
