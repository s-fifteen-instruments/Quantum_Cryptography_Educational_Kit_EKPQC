'''
Description: Python wrapper program to send a sequence of 16 bit keys (Alice)
without key sifting (it will be done manually).

Usage: Used in conjunction with `send_key.py`. The 'recv' program must be
started first before the 'send' program.

Options: python send_key.py 

        -h, --help            show this help message and exit
        --serial SERIAL     Sets the serial address of the Arduino

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

# Function to convert to hex, with a predefined nbits
def tohex(val, nbits):
  return hex((val + (1 << nbits)) % (1 << nbits))

# Other parameters declarations
baudrate = 38400      # Default in Arduino
timeout = 0.1        # Serial timeout (in s).

# Opens the sender side serial port
sender = serial.Serial(serial_addr, baudrate, timeout=timeout)

# Wait until the serial is ready
# Note: for some computer models, particularly MacOS, the program cannot
# talk to the serial directly after openin. Need to wait 1-2 second.
print("Opening the serial port...")
time.sleep(2)
print("Done\n")

# Starts the program
print("Alice, Are you ready? This is the key sender program.")
print("Randomising key bits and basis bits using Arduino")

# Randomising the sequence
sender.write('RNDSEQ '.encode())

# Block until receive reply
while True:
    if sender.in_waiting:
        print(sender.readlines()[0].decode()) # Should display OK
        break

print("Arduino says he/she likes to choose the following bits:")

# Find out what is the key
sender.write('SEQ? '.encode())

# Block until receive 1st reply
while True:
    if sender.in_waiting:
        reply_str = sender.readlines()[0][:-1].decode() # Remove the /n
        break

# Obtain the binary string repr for val and bas bits
val_str = ""
bas_str = ""
for bit in reply_str:
    val_str += str(int(bit) // 2)
    bas_str += str(int(bit) % 2)

# Giving the reply in HEX format
val_hex = tohex(int("0b"+val_str, 0), 16) # Get int, and convert to 16 bit hex
bas_hex = tohex(int("0b"+bas_str, 0), 16) # Get int, and convert to 16 bit hex
print("Value bits (in hex):", val_hex[2:].zfill(4))
print("Basis bits (in hex):", bas_hex[2:].zfill(4))

# Run the sequence
print("\nRunning the sequence...")
sender.write('TXSEQ '.encode())

# Block until receive reply
while True:
    if sender.in_waiting:
        print(sender.readlines()[0].decode()) # Should display OK
        break

# Print last statement and exits the program
print("Task done. Please perform key sifting with Bob via public channel.")
