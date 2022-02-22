'''
Python wrapper program to send a string through the IR channel with
the NEC-string protocol.
Author: Qcumber 2018
'''

import serial
import sys
import time

# Obtain device location
devloc_file = '../devloc_classical.txt'
with open(devloc_file) as f:
    content = f.readlines()[0]
    if content[-1] == '\n':  # Remove an extra \n
        content = content[:-1]
serial_addr = content

# Other parameters declarations
baudrate = 38400      # Default in Arduino
rep_wait_time = 0.3  # Wait time between packets (in s).
timeout = 0.1        # Serial timeout (in s).

# Opens the sender side serial port
sender = serial.Serial(serial_addr, baudrate, timeout=timeout)

# Wait until the serial is ready
# Note: for some computer models, particularly MacOS, the program cannot
# talk to the serial directly after openin. Need to wait 1-2 second.
print("Opening the serial port...")
time.sleep(2)
print("Done\n")

while True:
    try:
        msg_string = "\n" +\
                     "NEC-string Protocol Sender Qcumber v1.00 \n" +\
                     "To exit the program, use Ctrl+C \n" +\
                     "Write your message here: \n"
        tosend_string = input(msg_string)
        # Iterate and send the string
        sender.write('SEND '.encode()) # Flag to send
        sender.write('\x02\x02\x02\x02'.encode()) # Start of text
        time.sleep(rep_wait_time)
        str_ptr = 0
        max_str = len(tosend_string)
        while True:
            str_packet = tosend_string[str_ptr:str_ptr+4]
            sender.write('SEND '.encode()) # Flag to send
            sender.write(str_packet.encode())
            sys.stdout.write("\r{0}    ".format("Sending: "+str_packet))
            sys.stdout.flush()
            str_ptr += 4
            time.sleep(rep_wait_time)
            if str_ptr >= max_str:
                sender.write('SEND '.encode()) # Flag to send
                sender.write('\x03\x03\x03\x03'.encode()) # End of text
                time.sleep(rep_wait_time)
                sys.stdout.write("\r{0}\n".format("Sending done!"))
                sys.stdout.flush()
                break
    except NameError:   # Catches nonsense input
        print ("Input error. Please try again!")
        pass    # Loop back again
    except KeyboardInterrupt:
        print ("\nThank you for using the program!")
        sys.exit()  # Exits the program
