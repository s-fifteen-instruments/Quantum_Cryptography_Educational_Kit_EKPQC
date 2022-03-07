'''
Description: Python wrapper program to receive a string through the IR channel with
the NEC-string protocol. Use this program to chat with another party over the IR channel!

Usage: Both parties who wish to chat should start this program. The program starts in 
sending mode, hit 'Enter' to switch to receiving mode and vice versa. To send message,
type in message while in sending mode and hit 'Enter'. Use 'Ctrl+C' to exit the program.

Options: python chatting.py [-h]

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


# Other parameters declarations
baudrate = 38400      # Default in Arduino
rep_wait_time = 0.3  # Wait time between packets (in s).
timeout = 0.1        # Serial timeout (in s).

# Opens the device side serial port
device = serial.Serial(serial_addr, baudrate, timeout=timeout)

# Wait until the serial is ready
# Note: for some computer models, particularly MacOS, the program cannot
# talk to the serial directly after openin. Need to wait 1-2 second.
print("Opening the serial port...")
time.sleep(2)
print("Done\n")

print("Qcumber ChatBox v1.00")
print("To exit the program, use Ctrl+C")

# Always listening, except when it is not...
while True:
    try:
        msg_string = "\n" +\
                     "You are now in sending mode. To change to listening mode, press ENTER.\n" +\
                     "Write the message you want to send below: \n"
        tosend_string = input(msg_string)
        if tosend_string == "": # Nothing to send through
            pass
        else:   # Send the message lor
            # Iterate and send the string
            device.write('SEND '.encode()) # Flag to send
            device.write(b'\x02\x13\x13\x13') # Start of text
            time.sleep(rep_wait_time)
            str_ptr = 0
            max_str = len(tosend_string)
            while True:
                str_packet = tosend_string[str_ptr:str_ptr+4]
                device.write('SEND '.encode()) # Flag to send
                device.write(str_packet.encode())
                sys.stdout.write("\r{0}    ".format("Sending: "+str_packet))
                sys.stdout.flush()
                str_ptr += 4
                time.sleep(rep_wait_time)
                if str_ptr >= max_str:
                    device.write('SEND '.encode()) # Flag to send
                    device.write(b'\x03\x03\x03\x03') # End of text
                    time.sleep(rep_wait_time)
                    sys.stdout.write("\r{0}\n".format("Sending done!"))
                    sys.stdout.flush()
                    break
        msg_string = "\n" +\
                     "You are now in listening mode.\n" +\
                     "Waiting to receive the message... \n"
        print (msg_string)
        state = 0 # 0 : waiting for STX, 1 : transmitting/ wait for ETX
        device.reset_input_buffer() # Flush all the garbages
        device.write('RECV '.encode()) # Flag to recv
        while True:
            if device.in_waiting:
                hex_string = device.read(8)
                device.write('RECV '.encode()) # Flag to recv
                # Looking for start of text
                if hex_string[:7] == b'2131313':
                    print ("--- START OF TEXT ---")
                    state = 1
                elif state == 1:
                    try:
                        # Looking for end of text
                        if hex_string == b'3030303':
                            device.write('#'.encode()) # Flag to end listening
                            print ("\n--- END OF TEXT ---")
                            break
                        # Check and modify the length of string to 8 HEX char
                        hex_string = hex_string.decode()
                        if len(hex_string) < 8:
                            hex_string = hex_string.zfill(8)
                        # Convert to ASCII string
                        hex_list= list(map(''.join, list(zip(*[iter(hex_string)]*2))))
                        ascii_string = "".join([chr(int("0x"+each_hex,0)) for each_hex in hex_list])
                        sys.stdout.write(ascii_string)
                        sys.stdout.flush()
                    except ValueError:
                        print("\n ERROR! UNABLE TO DECODE STRING!")
    except KeyboardInterrupt:
        device.write('#'.encode()) # Flag to force end listening
        print ("\nThank you for using the program!")
        sys.exit()  # Exits the program
