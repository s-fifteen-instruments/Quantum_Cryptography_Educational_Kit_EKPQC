'''
Description: Python wrapper program to send 32 bits QKD keys via
quantum and classial channel.

Usage: Used in conjunction with `send_32bitQKD.py`. The 'recv' program
must be started first before the 'send' program.

Options: python recv_32bitQKD.py 

        -h, --help            show this help message and exit
        --cserial CSERIAL     Sets the serial address of the Classical Arduino
        --qserial QSERIAL     Sets the serial address of the Quantum Arduino
        --threshold THRESHOLD
                            Sets the threshold value for basis differentiation

Author: Qcumber 2018

Version: 1.0
'''

import serial
import sys
import time
import numpy as np
import argparse # For running the script with options

my_parser = argparse.ArgumentParser()
my_parser.add_argument('--cserial', action='store', type=str, required=True, help='Sets the serial address of the Classical Arduino')
my_parser.add_argument('--qserial', action='store', type=str, required=True, help='Sets the serial address of the Quantum Arduino')
my_parser.add_argument('--threshold', action='store', type=int, required=True, help='Sets the threshold value for basis differentiation')
args = my_parser.parse_args()

# Get the serial address
serial_addrC = vars(args).get('cserial') #contentC
serial_addrQ = vars(args).get('qserial') #contentQ
# Parameter
rep_wait_time = 0.3  # Wait time between packets (in s).
threshold = vars(args).get('threshold') # Threshold for basis differentiation.

''' Helper functions '''

# Function to convert to hex, with a predefined nbits
def tohex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))

def send4BytesC(message_str):
    if len(message_str) == 4:
        deviceC.write('SEND '.encode()) # Send identifier [BEL]x3 + B
        deviceC.write(b'\x07\x07\x07' + 'B'.encode()) # This is Bob (receiver)
        time.sleep(rep_wait_time)
        deviceC.write('SEND '.encode()) # Flag to send
        deviceC.write(message_str.encode())
        print(message_str)
    else:
        print("The message is not 4 bytes. Please check again")

def recv4BytesC():
    deviceC.reset_input_buffer() # Flush all the garbages
    deviceC.write('RECV '.encode()) # Flag to recv (the header)
    state = 0   # 0: waiting for STX, 1: transmitting/ wait for ETX
    while True:            # Block until receives a reply
        if deviceC.in_waiting:
            hex_string = deviceC.read(8).decode()
            print(f'hex_string: {hex_string}') #Debug
            print("state:", state)
            if hex_string == '7070741':  # 07-[BEL], 41-A (Header from Alice)
                # print ("Received message!") # Debug
                deviceC.write('RECV '.encode())   # Receive the message
                state = 1
            elif state == 1:
                break
    # Convert to ASCII string
    hex_list = list(map(''.join, list(zip(*[iter(hex_string)]*2))))
    ascii_string = "".join([chr(int("0x"+each_hex,0)) for each_hex in hex_list])
    print(ascii_string)
    time.sleep(rep_wait_time) # Wait a bit so that "Eve" can listen more carefully :P
    return ascii_string

def recvKeyQ():
    print("Generating random basis choices...")
    # Randomising the sequence
    deviceQ.write('RNDBAS '.encode())
    # Block until receive reply
    while True:
        if deviceQ.in_waiting:
            print(deviceQ.readlines()[0].decode().strip()) # Should display OK
            break
    # Find out what is the key
    deviceQ.write('SEQ? '.encode())
    # Block until receive 1st reply
    while True:
        if deviceQ.in_waiting:
            bas_str = deviceQ.readlines()[0].decode().strip() # Remove the /n
            break
    # Run the sequence
    print("Running the sequence and performing measurement...")
    deviceQ.write('RXSEQ '.encode())
    # Block until receive reply
    while True:
        if deviceQ.in_waiting:
            mes_str = deviceQ.readlines()[0].decode().strip() # Remove the /n
            break
    print("Finished...")
    # Obtain the measured bits
    mes_arr = mes_str.split()
    res_str = ''
    for val in mes_arr:
        if int(val) > threshold: # Higher than threshold -> 0
            res_str += '0'
        else:               # Lower than threshold -> 1
            res_str += '1'
    print(res_str, bas_str)
    return res_str, bas_str

def keySiftBobC(resB_str, basB_str):
    # Get ready confirmation from Alice
    recv4BytesC()
    print("Alice is ready! Performing key sifting with Alice...")
    # Zeroth step: convert the bin string repr to 32 bit int
    resB_int = int("0b"+resB_str, 0)
    basB_int = int("0b"+basB_str, 0)
    # First step: send the basis choice to Alice
    basB_hex = tohex(basB_int, 16) # Get the hex from int
    send4BytesC(basB_hex[2:].zfill(4)) # Sends this hex to Bob
    # Second step: Wait for her reply...
    matchbs_hex = recv4BytesC()   # in hex
    matchbs_int = int("0x"+matchbs_hex, 0)
    # Fourth step: Perform key sifting (in binary string)
    matchbs_str = np.binary_repr(matchbs_int, width=16)
    siftmask_str = ''
    for i in range(16): # 16 bits
        if matchbs_str[i] == '0' :
            siftmask_str += 'X'
        elif matchbs_str[i] == '1':
            siftmask_str += resB_str[i]
    # Remove all the X'es
    siftkey_str = ''
    for bit in siftmask_str:
        if bit == 'X':
            pass
        else:
            siftkey_str += bit
    # Return the final sifted key
    print(siftmask_str, siftkey_str)
    return siftkey_str

# Other parameters declarations
baudrate = 38400      # Default in Arduino
timeout = 0.1        # Serial timeout (in s).

# Opens the sender side serial port
deviceC = serial.Serial(serial_addrC, baudrate, timeout=timeout)
deviceQ = serial.Serial(serial_addrQ, baudrate, timeout=timeout)

# Wait until the serial is ready
# Note: for some computer models, particularly MacOS, the program cannot
# talk to the serial directly after openin. Need to wait 1-2 second.
print("Opening the serial port...")
time.sleep(2)
print("Done\n")

# Secure key string (binary)
seckey_bin = ""
n_attempt = 1

# Start of the UI
print("Hi Bob, are you ready? Let's make the key!")

try:
    # Testing the public channel
    print("\nTesting the public channel...")

    print("Alice sends", recv4BytesC())
    print("You reply --OK!!--")
    send4BytesC("OK!!")

    print("\nPublic channel seems okay... Sending the quantum keys...")

    while True:
        print("\nAttempt", n_attempt)
        res_str, bas_str = recvKeyQ()
        key = keySiftBobC(res_str, bas_str)
        seckey_bin = seckey_bin + key
        if len(seckey_bin) >= 32: # If the key is longer than 32 bits, stop operation
            break
        else:
            print("Done! You've got", len(key), "bits. Total length:", len(seckey_bin), "bits.")
            n_attempt +=1

    print("DONE. The task is completed.")

    # You've got the key!
    seckey_bin = seckey_bin[:32] # Trim to 32 bits
    seckey_hex = tohex(int("0b"+seckey_bin, 0), 32)
    # Some intrepreter introduces L at the end (which probably means long). Will remove them (cosmetic reason)
    if seckey_hex[-1] == "L":
        seckey_hex = seckey_hex[:-1]
    print("The 32 bit secret key is (in hex):", seckey_hex[2:].zfill(8))
    print("\n Congrats. Use the key wisely. Thank you!")

except KeyboardInterrupt:
    # End of program
    deviceC.write('#'.encode()) # Flag to force end listening
    print ("\nProgram interrupted. Thank you for using the program!")
    sys.exit()  # Exits the program
