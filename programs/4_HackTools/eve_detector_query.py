"""Program to continuously query Eve's detector readings.
Useful for callibration and testing purposes. Program runs
indefinitely - use 'Ctrl + C' to stop program.

Author: JH
Date: Feb 2023

Sample command in windows CMD:
> python eve_detector_query.py --serial com11
"""

import serial
import time
import argparse # For running the script with options
import sys

# Select device com port
my_parser = argparse.ArgumentParser()
my_parser.add_argument('--serial', action='store', type=str, required=True, help='Sets the serial address of the Eve Arduino')
args = my_parser.parse_args()
ser = vars(args).get('serial')

baudrate = 38400
timeout = 0.1
dev = serial.Serial(ser,baudrate,timeout=timeout)

def main():
    try:
        while True:
            # Query device
            dev.write('volts? '.encode())
            time.sleep(0.1)
            # Get reply - repeat
            reply = dev.readlines()
            vals = [val.decode().strip() for val in reply]
            print(vals)
    except KeyboardInterrupt:
        print('Program closed.')
        sys.exit()

if __name__=='__main__':
    main()