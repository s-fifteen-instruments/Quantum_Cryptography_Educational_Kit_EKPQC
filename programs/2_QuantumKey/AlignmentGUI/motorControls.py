"""
Description: Package for servo motor controls. Python wrapper for Arduino serial commands 
to talk to the motor. Contains a single 'MotorControl' class.

Usage: Only for Alice and Bob. Slight modifications will need to be made to talk to Eve's motors.

Authors: Qcumber 2018, Xi Jie

Version: 1.0
"""
from turtle import write_docstringdict
import serial
import time

class MotorControl(object):
# Module for communicating with the arduino analog pin

	def __init__(self, port):
		self.baudrate = 38400 # Arduino baudrate
		self.serial = serial.Serial(port = port, baudrate = self.baudrate, timeout=3)
		stuck_flag = True
		while stuck_flag:
			self.serial.write('ANG? '.encode())
			if not self.serial.in_waiting:
				# print("Stuck... Retrying")
				if not self.serial.isOpen():
					self.serial = serial.Serial(port, timeout=3)
				continue
			else:
				time.sleep(1)
				self.serial.reset_input_buffer()
				print("Program Launched Successfully")
				stuck_flag = not stuck_flag

	def close_port(self):
		if self.serial.is_open:
			self.serial.close()

	def get_voltage(self):
		self.serial.write('VOLT? '.encode())
		voltage_bit = float(self.readline_fix()) # Remove /n, change str to float
		voltage = voltage_bit/1024*5 # Convert from bit range to voltage (0-1023 --> 0-5V)
		return voltage

	def set_angle(self,angle):
		#Sets the absolute angle of the motor stepper
		curr_offset = self.get_offset()
		writeStr = 'SETANG ' + str(angle) + ' '
		self.serial.write(writeStr.encode())
		self.readline_fix()

	def get_angle(self):
		#Gets the absolute angle of the motor stepper
		self.serial.write('ANG? '.encode())
		angle = self.readline_fix()
		return angle

	def set_offset(self,angle):
		#Sets the offset angle of the motor stepper at H polarisation
		writeStr = 'SETHOF ' + str(angle) + ' '
		self.serial.write(writeStr.encode())
		self.readline_fix()

	def get_offset(self):
		#Gets the offset angle of the motor stepper at H polarisation
		self.serial.write('HOF? '.encode())
		angle = self.readline_fix()
		return angle

	def set_threshold(self,threshold):
		#Sets the detector threshold from 0-1023. 200 is approx. 1V
		writeStr = 'SETTH ' + str(threshold) + ' '
		self.serial.write(writeStr.encode())
		self.readline_fix()

	def get_threshold(self):
		#Gets the detector threshold from 0-1023. 200 is approx. 1V
		self.serial.write('TH? '.encode())
		threshold = self.readline_fix()
		return threshold

	def power_on(self):
		#Powers on laser
		self.serial.write("LASON ".encode())
		self.readline_fix()

	def readline_fix(self):
		while True:
			if self.serial.in_waiting:
				return self.serial.readline()[:-2].decode()

	def power_off(self):
		#Powers off laser
		self.serial.write("LASOFF ".encode())
		self.readline_fix()