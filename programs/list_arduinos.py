'''
Description: Script to return a list of open serial ports and their Arduino identities using the *IDN? command. If an unknown
serial device is connected, or does not respond to *IDN?, the script will move on to the next device after 10 tries.

Usage: Run program and wait for it to return the list.

Author: JH 2022

Version: 1.0
'''

import time
import serial
import glob
import sys
from tqdm import tqdm

def serial_ports():
	""" Lists serial port names

		:raises EnvironmentError:
			On unsupported or unknown platforms
		:returns:
			A list of the serial ports available on the system
	"""
	if sys.platform.startswith('win'):
		ports = ['COM%s' % (i + 1) for i in range(256)]
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		# this excludes your current terminal "/dev/tty"
		ports = glob.glob('/dev/tty[A-Za-z]*')
	elif sys.platform.startswith('darwin'):
		ports = glob.glob('/dev/tty.*')
	else:
		raise EnvironmentError('Unsupported platform')

	result = []
	for port in ports:
		try:
			s = serial.Serial(port)
			s.close()
			result.append(port)
		except (OSError, serial.SerialException):
			pass
	return result

ports = serial_ports()
print(f'The open ports are: {ports}')
print('Identifying ports, please wait...')

for index, port in enumerate(ports):
    try:
        # Adds Classical/Quantum identifier based on HELP text
        dev = serial.Serial(port, baudrate=38400, timeout=0.1)
        time.sleep(2) # Time for arduino ports to fully open
        dev.reset_input_buffer()
        dev.reset_output_buffer()
        dev.write("*IDN? ".encode())
        for i in tqdm(range(10)):
            if dev.in_waiting:
                response = dev.readlines()[0].decode().strip()
                ports[index] += " (" + response + ")"
                break
            time.sleep(0.05)
        dev.close()
    except:
        pass

print('Ports identified!')
print(ports)

