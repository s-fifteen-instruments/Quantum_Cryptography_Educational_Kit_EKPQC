"""
Description: GUI for Receiver program.
Created on May 2018, modified from the QITlab program.

Usage: Run on receiver's (Bob) side. Used to calibrate polarization
offsets and scan visibilities in tandem with `runSender.py`.

Author: Qcumber2018

Version: 1.0
"""

import sys
import glob
import serial
import time

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTimer
import motorControls as mc
import numpy as np

REFRESH_RATE = 100 # 100 ms
form_class = uic.loadUiType("guiRcv.ui")[0]

def insanity_check(number, min_value, max_value):
	''' To check whether the value is out of given range'''
	if number > max_value:
		return max_value
	if number < min_value:
		return min_value
	else:
		return number

# serial_ports function from:
# https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
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

class MyWindowClass(QMainWindow, form_class):

	def __init__(self, parent=None):

		self.offset = 0
		# Whether or not we started the device
		self.deviceRunning = False
		self.measuring = False

		# Whether or not we have scanned
		self.scanned = False

		# Declaring GUI window
		QMainWindow.__init__(self, parent)
		self.setupUi(self)
		self.initialiseParameters()

		# Bind event handlers (button & range)
		"""
		---List of Buttons---
		buttonStart : ON/OFF
		measureButton : Mesasure
		resetButton : Reset
		startScan : Scan
		setOffset : Set Offset
		autoOffset : autoOffset
		goToPol : go to polarisation
		goToAngle : go to relative angle
		setThButton: set detector threshold to detect incoming laser light
		"""
		self.buttonStart.clicked.connect(self.buttonStart_clicked)
		self.resetButton.clicked.connect(self.reset_params)
		self.measureButton.clicked.connect(self.measure)
		self.goToPol.clicked.connect(self.set_polarisation)
		self.goToAngle.clicked.connect(self.set_angle_gui)
		self.startScan.clicked.connect(self.start_scan)
		self.setOffset.clicked.connect(self.set_offset_gui)
		self.setThButton.clicked.connect(self.set_threshold_gui)


		# Gets a list of avaliable serial ports to connect to and adds to combo box
		self.ports = serial_ports()
		for index, port in enumerate(self.ports):
			try:
				# Adds Classical/Quantum identifier based on HELP text
				dev = serial.Serial(port, baudrate=38400, timeout=0.1)
				time.sleep(2)
				dev.reset_input_buffer()
				dev.reset_output_buffer()
				dev.write("*IDN? ".encode())
				while True:
					if dev.in_waiting:
						response = dev.readlines()[0].decode().strip()
						self.ports[index] += " (" + response + ")"
						break
				dev.close()
			except:
				pass
		self.deviceBox.addItems(self.ports)

		# Initialise plots
		self.plotWidget.plotItem.getAxis('left').setPen((0,0,0))
		self.plotWidget.plotItem.getAxis('bottom').setPen((0,0,0))
		labelStyle = {'font': 'Arial', 'font-size': '16px'}
		self.plotWidget.setLabel('left', 'Power', 'V',**labelStyle)
		self.plotWidget.setLabel('bottom', 'Absolute Angle', '',**labelStyle)


		# Set timer
		self.timer = QTimer()
		self.timer.timeout.connect(self.update_measure)
		self.timer.setInterval(REFRESH_RATE)
		self.timer.start()


		# Update status
		self.statusbar.showMessage("Ready to run ... Select your device!")

	def initialiseParameters(self):

		# Data for plotting
		self.xdata = np.arange(-180+self.offset,181+self.offset,1)
		self.ydata = np.zeros(361)
		self.plot = self.plotWidget.plot(self.xdata, self.ydata, pen={'color':(255,0,0),'width':2})
		# Some cosmetics
		self.plotWidget.setLimits(xMin = self.xdata[0], xMax = self.xdata[-1], yMin=0.0,yMax=5.0)
		self.plotWidget.getAxis('bottom').setTicks([[(value,str(value)) for value in np.arange(-180+self.offset,181+self.offset,45).tolist()]])
		self.plotWidget.showGrid(x=True)
		"""
		#Plotting the HDVA lines
		self.x_hdva = np.arange(0+self.offset,180+self.offset,45)
		self.plot2 = self.plotWidget.plot()
		"""
	###########
	# BUTTONS #
	###########
	def buttonStart_clicked(self):

		#Turning on device for the first time
		if not self.deviceRunning:
			# Start device
			self.motor = mc.MotorControl(str(self.deviceBox.currentText().split()[0]))
			# Initialising parameter and starting stuffs
			self.statusbar.showMessage("Device Running")
			self.buttonStart.setText("Stop")

			#Initialising the motors
			self.curr_angle = float(self.motor.get_angle())
			self.offset  = int(self.motor.get_offset())
			self.threshold = int(self.motor.get_threshold())
			self.update_threshold(self.threshold)
			self.update_offset(self.offset)
			self.update_angle(self.curr_angle)
			self.deviceRunning = not self.deviceRunning
		else:
			#Stop the device
			self.deviceRunning = not self.deviceRunning
			self.statusbar.showMessage("Device Stopped")
			# Change button appearance
			self.motor.close_port()
			self.buttonStart.setText("Start")
			self.labelPower.setText("OFF")

	def reset_params(self):
		#Resets the polarisation,angle and offset fields to zero
		self.statusbar.showMessage("Resetting Parameters... Please Wait")
		self.update_angle(0)
		self.update_offset(0)
		self.statusbar.showMessage("Resetting Parameters... Done")

	def start_scan(self):
		if self.deviceRunning:
			#Find how many plot points
			resolution = self.scanRes.value()
			number_of_points = 360 // (resolution)
			#Scan through the angles, plot graph and display plot
			self.xdata = np.arange(-180+self.offset,181+self.offset,resolution)
			self.ydata = np.zeros(number_of_points+1)
			read_count = 0
			self.statusbar.showMessage("Scanning... Please Wait")
			while(read_count != (number_of_points+1)):
				try:
					#Update angle on GUI
					self.update_angle(self.xdata[read_count])
					self.voltage_A0 = float(self.motor.get_voltage())
					power_str = str(self.voltage_A0)
					#self.labelPower.setText(power_str + " V")
					self.ydata[read_count] = self.voltage_A0
					read_count += 1
					print(self.xdata[read_count], power_str,sep='\t')
				except:
					# Sometime the serial channel needs to clear some junks
					pass
			self.scanned = True
			# Plot data
			self.plotWidget.setLimits(xMin = self.xdata[0], xMax = self.xdata[-1],yMin=0.0,yMax=5.0)
			self.plot.setData(self.xdata, self.ydata)
			self.plotWidget.getAxis('bottom').setTicks([[(value,str(value)) for value in np.arange(-180+self.offset,181+self.offset,45).tolist()]])
			self.plotWidget.showGrid(x=True)
			ymax = self.ydata.max()
			ymin = self.ydata.min()
			visibility = (ymax-ymin)/(ymax+ymin)
			self.visibilityLabel.setText(f"Visibility is {visibility:.4f}")
			self.statusbar.showMessage("Scanning... Done")
		else:
			self.labelPower.setText("OFF")

	"""
	def set_angle(self):
		#Change the absolute angle in GUI and here
		#Get angle on GUI
		angle_value = self.angleInput.value()
		self.statusbar.showMessage("Setting Angle... Please Wait")
		self.curr_angle = angle_value
		self.motor.set_angle(angle_value)
		self.statusbar.showMessage("Setting Angle... Done")
	"""
	def set_angle_gui(self):
		#Set absolute angle
		abs_angle = self.angleInput.value()
		self.update_angle(abs_angle)
		return None

	def update_angle(self,angle_value):
		#Change the absolute angle in GUI and here
		self.statusbar.showMessage("Updating Angle... Please Wait")
		self.curr_angle = angle_value
		self.angleInput.setValue(angle_value) #QDoubleSpinBox - See guiRcv.ui file
		self.motor.set_angle(angle_value)
		self.statusbar.showMessage("Updating Angle... Done")
		return None

	def set_threshold_gui(self):
		#Set detector threshold
		threshold = self.thInput.value()
		self.update_threshold(threshold)
		return None

	def update_threshold(self, threshold):
		#Change the threshold in GUI and here
		self.statusbar.showMessage("Updating Threshold... Please Wait")
		self.threshold = threshold #Internal variable
		self.thInput.setValue(threshold) #GUI Display
		self.motor.set_threshold(threshold) #Arduino
		self.statusbar.showMessage("Updating Threshold... Done")
		return None

	def update_offset(self,offset_value):
		#Change the angle in GUI and here
		self.statusbar.showMessage("Updating Offset... Please Wait")

		self.offset = offset_value
		self.offsetInput.setValue(offset_value)
		self.motor.set_offset(offset_value)
		self.statusbar.showMessage("Updating Offset... Done")
		return None

	def set_offset_gui(self):
		#Set offset angle at current angular position
		offset_value = self.offsetInput.value()
		self.update_offset(offset_value)
		return None

	def set_polarisation(self):
		#Set the polarisation
		#The polarisation number
		pol_number = self.polInput.value()
		self.update_angle(pol_number*45+self.offset)
		return None

	def measure(self):
		if self.deviceRunning:
			if not self.measuring:
				self.measuring = not self.measuring
				self.measureButton.setText("Stop Measure")
			else:
				self.measuring = not self.measuring
				self.measureButton.setText("Start Measure")
		else:
			self.measuring = False
			self.labelPower.setText("OFF")

	def update_measure(self):
		#If we are measuring
		if self.measuring:
			try:
				self.voltage_A0 = float(self.motor.get_voltage())
				power_str = '%.2f'%(self.voltage_A0)
				self.labelPower.setText(power_str + " V")
			except:
				# Sometime the serial channel needs to clear some junks
				pass
			#self.scanned = True
		else:
			self.labelPower.setText("OFF")

	def cleanUp(self):
		if self.deviceRunning:
			self.buttonStart_clicked()
		print("Closing the program ... Good bye!")
		self.deviceRunning = False
		time.sleep(0.5)

if __name__ == '__main__':

	app = QApplication(sys.argv)
	myWindow = MyWindowClass(None)
	myWindow.show()
	app.aboutToQuit.connect(myWindow.cleanUp)
	sys.exit(app.exec_())
