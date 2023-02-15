"""
while True:
    LOOP
    start input mode
    listen for input
    if no input:
        continue loop
    if input OR Enter key is hit:
        send input as message
        go to receving mode
    END LOOP

    LOOP
    start receive
    listen for messages being broadcasted
    if no message:
        continue loop
    if message OR Enter key is hit:
        print message to terminal
        go to input mode

    Keyboard interrupt to close the program

"""

import serial
import sys
import time
import argparse # For running the script with options
from threading import Thread

my_parser = argparse.ArgumentParser()
my_parser.add_argument('--serial', action='store', type=str, required=True, \
    help='Sets the serial address of the Arduino. E.g. COM6 or ttyACM0')

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
def chat():
    chatting_mode = 0 # 0 = sending, 1 = listening
    while True:
        if chatting_mode == 0:
            try:
                input_str = wait_for_input()
                print(f'input_string: {input_str}')
                if input_str == "":
                    pass
                else:
                    send_input(input_str, device)
                print('Switching chatting mode to 1')
                chatting_mode = 1
            except KeyboardInterrupt:
                device.write('#'.encode()) # Flag to force end listening
                print ("\nThank you for using the program!")
                sys.exit()  # Exits the program
        elif chatting_mode == 1:
            try:
                listen_for_message(device)
                print('Switching chatting mode to 0')
                chatting_mode = 0
            except KeyboardInterrupt:
                device.write('#'.encode())
                print ("\nThank you for using the program!")
                sys.exit()
    


def wait_for_input():
    msg_string = "\n" +\
                     "You are now in sending mode.\n" +\
                     "To change to listening mode, press ENTER.\n" +\
                     "Write the message you want to send below: \n"
    tosend_string = input(msg_string)
    return(tosend_string)

def send_input(input, device):
    device.write('SEND '.encode()) # Flag to send
    device.write(b'\x02\x13\x13\x13') # Start of text
    time.sleep(rep_wait_time)
    str_ptr = 0
    max_str = len(input)
    while True:
        str_packet = input[str_ptr:str_ptr+4]
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

def listen_for_message(device):
    msg_string = "\n" +\
                     "You are now in listening mode.\n" +\
                     "To change to sending mode, press ENTER.\n" +\
                     "Waiting to receive the message... \n"
    state = 0 # 0 : waiting for Unicode STX, 1 : transmitting/ wait for ETX
    device.reset_input_buffer() # Flush all the garbages
    device.write('RECV '.encode())
    i = 0
    while True:
        i+=1
        print(f'Listening Loop {i}')
        #input_str = input(msg_string) + "\n"
        if device.in_waiting:
            print(f'Entering DEVICE IN WAITING')
            hex_string = device.read(8)
            device.write('RECV '.encode())
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
        """Need to implement input as a separate thread. If not it
           blocks the listening loop from looping."""
        # if input_str == "\n":
        #     # To exit receiving mode
        #     print(f'Breaking from receiving mode')
        #     device.write('#'.encode())
        #     break
        # print('Reached end of TRUE loop')

if __name__ == "__main__":
    chat()