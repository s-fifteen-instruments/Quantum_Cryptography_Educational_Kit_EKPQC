import serial
import time
import datetime
import numpy as np

sender_path = 'COM6'
receiver_path = 'COM3'
baud_rate = 38400
timeout = 0.1
file_name = 'qwp_test.csv'

send = serial.Serial(sender_path, baudrate = baud_rate, timeout = timeout)
recv = serial.Serial(receiver_path, baudrate = baud_rate, timeout = timeout)

def circ_test():
    # Write to motor
    angles = np.linspace(0, 360, 30, dtype=np.int64)
    cmd_str = 'setang '
    with open(file_name, 'a+') as f:
            print('{},{}'.format('ANGLE', 'VOLT'), file=f)
    for angle in angles:
        send.write((cmd_str + str(angle) + ' ').encode())
        time.sleep(0.4) # Time for motor to turn, not sure if required but to be safe
        print('setang ' + str(angle))
        send.reset_input_buffer()
         # Turn laser on
        send.write('lason '.encode())
        time.sleep(0.1)
        send.reset_input_buffer()
        # Get volt reading
        recv.write('volt? '.encode())
        time.sleep(0.1)
        volt = recv.readline().decode().strip()
        # Turn laser off
        send.write('lasoff '.encode())
        time.sleep(0.1)
        send.reset_input_buffer()
        # Get background reading
        recv.write('volt? '.encode())
        time.sleep(0.1)
        volt_bg =recv.readline().decode().strip()
        # Actual reading
        try:
            volt = float(volt) - float(volt_bg)
            with open(file_name, 'a+') as f:
                print('{},{}'.format(str(angle), str(volt)), file=f)
        except:
            print('Skipping loop ' + str(angle))
            pass

circ_test()