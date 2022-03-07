'''
Description: Python wrapper program to send commands to Arduino Classical to turn sender
LED on and off. The purpose is to serve as a simple demonstration of how a
phone camera can capture wavelengths that the eye cannot. The sender LED used
in the Mar 2022 iteration emits 940nm light.

Usage: Start the program in a command line (eg. Command Prompt for Windows). 
Enter the commands 'LEDON ' or 'LEDOFF '. Note the space after the letters - 
it is used to indicate the end of the command and the computer can begin to 
process the whole of message. The commands are also not case-sensitive, you may
try this out with any combination of capital and non-capital letters. All 
commands that do not fit the above description will be met with an 'Unknown
Command'.

Options: python chatting.py

        -h, --help       show this help message and exit
        --serial SERIAL  Sets the serial address of the Arduino

Author: JH 2022

Version: 1.0
'''

import serial
import sys
import time
import argparse # For running the script with options

# Obtain device location
my_parser = argparse.ArgumentParser()
my_parser.add_argument('--serial', action='store', type=str, required=True, help='Sets the serial address of the Arduino')
args = my_parser.parse_args()
serial_addr = vars(args).get('serial')

# Other parameters declarations
baudrate = 38400      # Default in Arduino
timeout = 0.1        # Serial timeout (in s).

device = serial.Serial(serial_addr, baudrate, timeout=timeout)

# Wait until the serial is ready
# Note: for some computer models, particularly MacOS, the program cannot
# talk to the serial directly after openin. Need to wait 1-2 second.
print("Opening the serial port...")
time.sleep(2)
print("Done\n")

print("LED basic on/off program")
print("\"LEDON\" and \"LEDOFF\" to turn the LED on and off respectively")
print("Commands are not case-sensitive")
print("To exit the program, use Ctrl+C\n")

while True:
    try:
        x=input("Enter command here: ")
        # Convert user input to lower case and check for a match
        if x.lower() == "ledon" or x.lower() == "ledoff":
            device.write(x.encode())
            time.sleep(0.1)
            # Read response, convert bits to string, remove EOL characters
            response = device.readlines()[0].decode().strip()
            print(response)
            continue
        else:
            print("Unknown command")
            continue
    except NameError:
        print("Input error. Please try again!")
        pass
    except KeyboardInterrupt:
        print ("\nKeyboard Interrupt - Exiting...thank you for using the program!")
        # Exits the program
        sys.exit()