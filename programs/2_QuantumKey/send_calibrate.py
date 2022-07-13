'''
Description: Python wrapper program to calibrate the quantum / polarisation
signal transmission (for sender).

Usage: This program is used in tandem with `send_calibrate.py`. The receiver (Bob)
must start `recv_calibrate.py` first before the sender (Alice) starts `send_calibrate.py`
on their end. 

Options: python recv_calibrate.py

        -h, --help       show this help message and exit
        --serial SERIAL  Sets the serial address of the Arduino

Author: Qcumber 2018

Version: 1.0
'''

import serial
import sys
import time
import argparse # For running the script with options

my_parser = argparse.ArgumentParser()
my_parser.add_argument('--serial', action='store', type=str, required=True, help='Sets the serial address of the Arduino')

# Get the serial address
args = my_parser.parse_args()
serial_addr = vars(args).get('serial')

# Parameters
# 0,1,2,3 - H,V,D,A respectively
sender_seq = '0123012301230123 '

# Other parameters declarations
baudrate = 38400      # Default in Arduino
timeout = 0.1        # Serial timeout (in s).

# Starts the program
print("Polarisation Calibrator (Sender)")
print("Uploading sequence to Arduino...")

# Opens the sender side serial port
sender = serial.Serial(serial_addr, baudrate, timeout=timeout)

# Wait until the serial is ready
# Note: for some computer models, particularly MacOS, the program cannot
# talk to the serial directly after openin. Need to wait 1-2 second.
print("Opening the serial port...")
time.sleep(2)
print("Done\n")

# Flushing buffers
print("Flushing serial port")
sender.reset_input_buffer()
sender.reset_output_buffer()
print("Flushed")

# Send the sequence
print('Uploading polarization sequence...')
seq = 'POLSEQ ' + sender_seq
sender.write(seq.encode())

# Block until receive reply
while True:
    if sender.in_waiting:
        print((sender.readlines()[0].decode())) # Should display OK
        break

# Run the sequence
# Polarization state always returns to 1 at the end
# This is defined in the Arduino code
print("Running the sequence...")
txseq = 'TXSEQ '
sender.write(txseq.encode())

# Block until receive reply
while True:
    if sender.in_waiting:
        print((sender.readlines()[0].decode())) # Should display OK
        break

# Print last statement and exits the program
print("Task done. Look at Receiver for the calibration result")
