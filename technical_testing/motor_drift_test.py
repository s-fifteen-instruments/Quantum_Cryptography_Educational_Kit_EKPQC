"""
Code to query two usb ports continuously for motor angle.
To test motor drift while power is on, and whether the lopsided polarizer affects drift.
The drift seems to be on the order of 1-2 minutes? Querying every 3s or so should give me a good picture.
"""

import time
import serial
from datetime import datetime

port1 = 'COM6'
port2 = 'COM3'
baud_rate = 115200
timeout = 0.1
period = 1 # seconds
file_name = 'motor_drift1.csv'

print("Opening the serial port...")
time.sleep(2) # Ports take longer to fully open on some systems.
print("Done\n")

# Initiate ports
dev1 = serial.Serial(port1, baudrate=baud_rate, timeout=timeout)
dev2 = serial.Serial(port2, baudrate=baud_rate, timeout=timeout)

# Flushing buffers
print("Flushing serial port")
dev1.reset_input_buffer()
dev1.reset_output_buffer()
dev2.reset_input_buffer()
dev2.reset_output_buffer()
print("Flushed")

# Write to both motors every period and get response
while True:
    dev1.write('ang? '.encode())
    dev2.write('ang? '.encode())
    time.sleep(0.1)
    ang1 = dev1.readlines()[0].decode()
    ang2 = dev2.readlines()[0].decode()
    now = datetime.now()
    nowstr = str(now).split[-1]
    with open(file_name, 'a+') as f:
        print('{},{},{}'.format(now, ang1, ang2))
    time.sleep(period)

