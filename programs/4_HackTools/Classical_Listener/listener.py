'''
Python wrapper program to eavesdrop on the IR channel (continously)
Author: Qcumber 2018
'''

import serial
import sys
import time

# Obtain device location
# devloc_file = '../../devloc_classical.txt'
# with open(devloc_file) as f:
#     content = f.readlines()[0]
#     if content[-1] == '\n':  # Remove an extra \n
#         content = content[:-1]
serial_addr = 'COM9'

# Other parameters declarations
baudrate = 38400      # Default in Arduino
timeout = 0.1        # Serial timeout (in s).

# Opens the sender side serial port
receiver = serial.Serial(serial_addr, baudrate, timeout=timeout)

# Wait until the serial is ready
# Note: for some computer models, particularly MacOS, the program cannot
# talk to the serial directly after openin. Need to wait 1-2 second.
print("Opening the serial port...")
time.sleep(2)
print("Done\n")

print("IR Listener for Qcumbers")
print("To exit the program, use Ctrl+C")
print("Waiting for data ... ")

receiver.reset_input_buffer() # Flush all the garbages
receiver.write('RECV '.encode()) # Flag to recv

while True:
    try:
        if receiver.in_waiting:
            hex_string = receiver.read(8).decode()
            # print(f'\nhex string: {hex_string}')   
            # Looking for any kind of headers
            if hex_string == '2131313':
                print ("\n--- START OF TEXT ---")
            elif hex_string == '3030303':
                print ("\n--- END OF TEXT ---")
            elif hex_string == '7070741':
                print ("\nIncoming message from Alice:")
            elif hex_string == '7070742':
                print ("\nIncoming message from Bob:")
            else:
                try:
                    # Check and modify the length of string to 8 HEX char
                    if len(hex_string) < 8:
                        hex_string = hex_string.zfill(8)
                    # Convert to ASCII string
                    hex_list= list(map(''.join, list(zip(*[iter(hex_string)]*2))))
                    ascii_string = "".join([chr(int("0x"+each_hex,0)) for each_hex in hex_list])
                    sys.stdout.write(ascii_string)
                    sys.stdout.flush()
                except ValueError:
                    print("\n ERROR! UNABLE TO DECODE STRING!")
            #Flag to recv (again)
            receiver.write('RECV '.encode()) 

    except KeyboardInterrupt:
        receiver.write('#'.encode()) # Flag to force end listening
        print ("\nThank you for using the program!")
        sys.exit()  # Exits the program
