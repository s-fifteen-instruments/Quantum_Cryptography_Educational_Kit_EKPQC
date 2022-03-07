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
import numpy as np
import argparse # For running the script with options

my_parser = argparse.ArgumentParser()
my_parser.add_argument('--serial', action='store', type=str, required=True, help='Sets the serial address of the Arduino')

# Get the serial address
args = my_parser.parse_args()
serial_addr = vars(args).get('serial')

# Parameters
recv_seq = '0000111122223333 '
#recv_seq = '0123012301230123 '

# Other parameters declarations
baudrate = 38400    # Default in Arduino
timeout = 0.1        # Serial timeout (in s).

# Starts the program
print("Polarisation Calibrator (Receiver)")
print("Uploading sequence to Arduino...")

# Opens the sender side serial port
receiver = serial.Serial(serial_addr, baudrate, timeout=timeout)

# Wait until the serial is ready
# Note: for some computer models, particularly MacOS, the program cannot
# talk to the serial directly after openin. Need to wait 1-2 second.
print("Opening the serial port...")
time.sleep(2)
print("Done\n")

print("Flushing serial port")
receiver.reset_input_buffer()
receiver.reset_output_buffer()
print("Flushed")

# Send the sequence
print('Uploading polarization sequence...')
seq = 'POLSEQ ' + recv_seq
#print(('seq is:{}'.format(seq)))
receiver.write(seq.encode())

# Block until receive reply
while True:
    if receiver.in_waiting:
        print((receiver.readlines()[0].decode())) # Should display OK
        break

# Run the sequence
print("Listen for incoming signal...")
rxseq = 'RXSEQ '
receiver.write(rxseq.encode())

# Block until receive 1st reply
while True:
    if receiver.in_waiting:
        # print('in_wait'.format(receiver.in_waiting))
        # time.sleep(100)
        #print("entering if block")
        tmp = receiver.readlines() # Should display lots of nonsense
        #print(("text:", tmp))
        # for val in tmp:
        #     print(f'val:{val}')
        tmp2 = tmp[0].decode()
        #print(("text2:", tmp2))
        res_str = tmp2
        #print(('res_str is: {}'.format(res_str)))
        if res_str:
            try:
                resA = np.array(res_str.split()).astype(np.int32)
                #print(("resA is: {}".format(str(resA))))
            except ValueError as e: # To ignore all the debug lines
                print(e)
                continue
        print("Measurement done")
        print(" ")
        break

# Printing cosmetics
print("                    Receiver         ")
print("           |  H  |  D  |  V  |  A  | ")
print(("       | H | " + str(resA[0]).rjust(3,' ') + " | " + str(resA[1]).rjust(3,' ') + " | " + str(resA[2]).rjust(3,' ') + " | "+ str(resA[3]).rjust(3,' ') + " | "))
print(("Sender | D | " + str(resA[4]).rjust(3,' ') + " | " + str(resA[5]).rjust(3,' ') + " | " + str(resA[6]).rjust(3,' ') + " | "+ str(resA[7]).rjust(3,' ') + " | "))
print(("       | V | " + str(resA[8]).rjust(3,' ') + " | " + str(resA[9]).rjust(3,' ') + " | " + str(resA[10]).rjust(3,' ') + " | "+ str(resA[11]).rjust(3,' ') + " | "))
print(("       | A | " + str(resA[12]).rjust(3,' ') + " | " + str(resA[13]).rjust(3,' ') + " | " + str(resA[14]).rjust(3,' ') + " | "+ str(resA[15]).rjust(3,' ') + " | "))
print(" ")

# Calculating the mean
mean = np.average(resA)
print(("  The mean is " + str(round(mean, 3))))

# Construct the result array-ish
norm_fac = 2 * mean
theoA = norm_fac*np.array([1, 0.5, 0, 0.5, 0.5, 1, 0.5, 0, 0, 0.5, 1, 0.5, 0.5, 0, 0.5, 1])
delta = np.abs(theoA-resA)
deviation = np.sum(delta) / (16 * mean)
print(("  Signal degradation is " + str(round(deviation, 3))))
print("  ")

# Print last statement and exits the program
