#!/usr/bin/python

from __future__ import print_function
import argparse

from dyson_pure_link_device import DysonPureLink
from value_types import FanMode, StandbyMonitoring

if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-fan')
    args_parser.add_argument('-standby')
    args_parser.add_argument('-osc')
    args_parser.add_argument('-speed')
    args = args_parser.parse_args()

    # Start new instance of Dyson Pure Link Device
    dyson_pure_link = DysonPureLink()

    # Parse and print config file
    print('Parsed config file: ', dyson_pure_link.parse_config())

    # Connect device and print result
    print('Connected: ', dyson_pure_link.connect_device())

    # Get and print state and sensors data
    for entry in dyson_pure_link.get_data():
        print(entry)

    # Set Fan mode command
    if args.fan:
        print('Testing fan mode')
        dyson_pure_link.set_fan_mode(args.fan)
        for entry in dyson_pure_link.get_data():
            print(entry)

    # Set Standby monitoring command
    if args.standby:
        print('Testing standby mode')
        dyson_pure_link.set_standby_monitoring(args.standby)
        for entry in dyson_pure_link.get_data():
            print(entry)

    # Set Fan speed command
    if args.speed:
        print('Testing fan speed')
        dyson_pure_link.set_fan_speed(args.speed)
        for entry in dyson_pure_link.get_data():
            print(entry)

    # Set Oscillation command
    if args.osc:
        print('Testing oscillation')
        dyson_pure_link.set_oscillation(args.osc)
        for entry in dyson_pure_link.get_data():
            print(entry)

    # Disconnect device (IMPORTANT) and print result
    print('Disconnected: ', dyson_pure_link.disconnect_device())
