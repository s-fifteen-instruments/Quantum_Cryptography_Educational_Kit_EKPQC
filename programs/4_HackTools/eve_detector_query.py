"""Program to continuously query Eve's detector readings.
Useful for callibration and testing purposes.
"""

import serial
import time
import argparse # For running the script with options

# Select device com port
my_parser = argparse.ArgumentParser()
my_parser.add_argument('--serial', action='store', type=str, required=True, help='Sets the serial address of the Eve Arduino')
args = my_parser.parse_args()
ser = vars(args).get('serial')

baudrate = 38400
timeout = 0.1
dev = serial.Serial(ser,baudrate,timeout=timeout)

def main():
    while True:
        # Query device
        dev.write('volts? '.encode())
        time.sleep(0.1)
        # Get reply - repeat
        reply = dev.readlines()
        vals = [val.decode().strip() for val in reply]
        print(vals)

if __name__=='__main__':
    main()