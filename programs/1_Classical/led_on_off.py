'''
Python wrapper program to send commands to Arduino Classical to turn sender
LED on and off. The purpose is to serve as a simple demonstration of how a
phone camera can capture wavelengths that the eye cannot. The sender LED used
in the Mar 2022 iteration emits 940nm light.
Author: JH 2022
'''

import serial
import sys
import time

# Obtain device location
devloc_file = '../devloc_classical.txt'
# with open(devloc_file) as f:
#     content = f.readlines()[0]
#     if content[-1] == '\n':  # Remove an extra \n
#         content = content[:-1]
serial_addr = 'COM5'

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
print("To exit the program, use Ctrl+C\n")

while True:
    try:
        x=input("Enter command here: ")
        if x.lower() == "ledon" or x.lower() == "ledoff":
            device.write(x.encode())
            time.sleep(0.1)
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
        sys.exit()  # Exits the program