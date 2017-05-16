"""Releases any stepper motors"""
import sys
import json

def output_message(message):
    """Print the provided input & flush stdout so parent process registers the message"""
    print message
    sys.stdout.flush()


def output_json_message(json_input):
    """Print the provided json & flush stdout so parent process registers the message"""
    serialized_json = json.dumps(json_input, separators=(',', ':'))
    output_message(serialized_json)

def main():
    """Releases motors"""
    output_json_message(
        {'type': "update", 'status': "complete", 'msg': "Released Stepper Motors!"})

if __name__ == '__main__':
    main()
