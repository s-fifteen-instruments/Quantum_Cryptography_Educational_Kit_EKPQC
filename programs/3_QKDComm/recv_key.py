'''
Description: Python wrapper program to receive a sequence of 16 bit keys (Bob)
without key sifting (it will be done manually).

Usage: Used in conjunction with `send_key.py`. The 'recv' program must be
started first before the 'send' program.

Options: python recv_key.py 

        -h, --help            show this help message and exit
        --serial SERIAL     Sets the serial address of the Arduino
        --threshold THRESHOLD
                            Sets the threshold value for basis differentiation

Author: Qcumber 2018

Version: 1.0
'''

import serial
import sys
import time
import argparse # For running the script with options

my_parser = argparse.ArgumentParser()
my_parser.add_argument('--serial', action='store', type=str, required=True, help='Sets the serial address of the Arduino')
my_parser.add_argument('--threshold', action='store', type=int, required=True, help='Sets the threshold value for basis differentiation')
args = my_parser.parse_args()

# Get the serial address
serial_addr = vars(args).get('serial')
baudrate = 38400      # Default in Arduino
timeout = 0.1        # Serial timeout (in s).
# Parameter
rep_wait_time = 0.3  # Wait time between packets (in s).
threshold = vars(args).get('threshold') # Threshold for basis differentiation.

# Function to convert to hex, with a predefined nbits
def tohex(val, nbits):
  return hex((val + (1 << nbits)) % (1 << nbits))

# Opens the receiver side serial port
receiver = serial.Serial(serial_addr, baudrate, timeout=timeout)

# Wait until the serial is ready
# Note: for some computer models, particularly MacOS, the program cannot
# talk to the serial directly after openin. Need to wait 1-2 second.
print("Opening the serial port...")
time.sleep(2)
print("Done\n")

# Starts the program
print("Bob, Are you ready? This is the key receiver program.")
print("Randomising basis bits using Arduino")

# Randomising the sequence
receiver.write('RNDBAS '.encode())

# Block until receive reply
while True:
    if receiver.in_waiting:
        print((receiver.readlines()[0].decode())) # Should display OK
        break

print("Arduino says he/she likes to choose the following bits:")

# Find out what is the key
receiver.write('SEQ? '.encode())

# Block until receive 1st reply
while True:
    if receiver.in_waiting:
        bas_str = receiver.readlines()[0].decode()[:-1] # Remove the /n
        break

# Giving the reply in HEX format
bas_hex = tohex(int("0b"+bas_str, 0), 16) # Get int, and convert to 16 bit hex
print(("Basis bits (in hex):", bas_hex[2:].zfill(4)))

# Run the sequence
print("\nRunning the sequence and performing measurement...")
receiver.write('RXSEQ '.encode())

# Block until receive reply
while True:
    if receiver.in_waiting:
        meas_str = receiver.readlines()[0].decode()[:-1] # Remove the /n
        break

# Obtain the measured bits
meas_arr = meas_str.split()
# print (meas_str)
res_str = ''
for val in meas_arr:
    # print (val)
    if int(val) > threshold: # Higher than threshold -> 0
        res_str += '0'
    else:               # Lower than threshold -> 1
        res_str += '1'

res_hex = tohex(int("0b"+res_str, 0), 16) # Get int, and convert to 16 bit hex
print(("Measurement result bits (in hex):", res_hex[2:].zfill(4)))
# print meas_arr # Debug
# print res_str # Debug

# Print last statement and exits the program
print("\nTask done. Please perform key sifting with Bob via public channel.")
