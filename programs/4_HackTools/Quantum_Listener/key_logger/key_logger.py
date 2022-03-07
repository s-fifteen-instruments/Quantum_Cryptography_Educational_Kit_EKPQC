'''
Description: Python wrapper program to eavesdrop on the quantum channel for Eve.

Usage: Start the program and wait. The photodiode readings will be logged into a .dat
file. The .dat file is automatically named with the current time.

Options:

  -h, --help       show this help message and exit
  --serial SERIAL  Sets the serial address of the Arduino

Author: Qcumber 2018

Version: 1.0
'''

import serial
import sys
import time
from datetime import datetime
import argparse # For running the script with options

my_parser = argparse.ArgumentParser()
my_parser.add_argument('--serial', action='store', type=str, required=True, help='Sets the serial address of the Arduino')

# Get the serial address
args = my_parser.parse_args()
serial_addr = vars(args).get('serial')

print("Eavesdropping... will record any voltages into a file")
print("To exit the program, use Ctrl+C \n")

# Other parameters declarations

# Serial 1
baudrate1 = 38400      # Default in Arduino
timeout1 = 0.1        # Serial timeout (in s).
refresh_rate= 0.05     # Minimum offset around 10 ms

# Serial 2
baudrate2 = 38400    # Default in Arduino
timeout2 = 0          # Serial timeout (in s).
# Some note (may be a bug in the future):
# The pyserial somehow does not properly respond to powermeter timeout
# I will just assume it to have 0 timeout, and let the blocking done
# by the other device's response time.

# Opens the receiver side serial port
ardu = serial.Serial(serial_addr, baudrate1, timeout=timeout1)

# Waiting until the serial device is open (for some computer models)
time.sleep(2)
print("Ready!\n")

# The filename is the current time
filename_tmp =  str(datetime.now().time())[:8]
tmp1 = filename_tmp.split(":")
filename = "".join(tmp1) + '.dat'
print(filename)
print("Logging the voltages into:", filename)

ardu.reset_input_buffer()   # Clear previous buffer
time_start = time.time()    # Get the starting time

while True:
    try:
        ardu.write("VOLTS? ".encode())
        # Block until receive the reply
        while True:
            if ardu.in_waiting:
                # Might not work exactly as expected yet, depending on the \r and \n the Arduino spits out
                byte_response1 = ardu.readline()
                byte_response2 = ardu.readline()
                volt_now1 = byte_response1.decode().strip()
                volt_now2 = byte_response2.decode().strip()
                break
        print(time.time()-time_start, volt_now1, volt_now2)
        # Write to a file
        with open(filename, "a+") as myfile:
            myfile.write(volt_now1 + " " + volt_now2 + " " + "\n")
        # Wait until the next time
        time.sleep(refresh_rate)
    except KeyboardInterrupt:
        print ("\nThank you for using the program!")
        sys.exit()  # Exits the program 
