#!/usr/bin/env python
"""
Created on May 2018

Modified from the QITlab program
@author: Qcumber2018

GUI for Receiver program 
"""

import sys
import glob
import time

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
import motorControls as mc
import serial
import numpy as np

REFRESH_RATE = 0.1 # 100 ms
form_class = uic.loadUiType("guiSnd.ui")[0]

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
        #self.laserOn = False
        # Whether or not we started the device
        self.deviceRunning = False
        self.laserOn = False
        # Whether or not we have scanned
        self.scanned = False


        # Declaring GUI window
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        #self.initialiseParameters()

        # Bind event handlers (button & range)
        """
        ---List of Buttons---
        buttonStart : ON/OFF
        resetButton : Reset
        setOffset : Set Offset
        goToPol : go to polarisation
        goToAngle : go to relative angle
        """
        self.buttonStart.clicked.connect(self.buttonStart_clicked)
        self.resetButton.clicked.connect(self.reset_params)
        self.goToPol.clicked.connect(self.set_polarisation)
        self.goToAngle.clicked.connect(self.set_angle_gui)
        self.setOffset.clicked.connect(self.set_offset_gui)
        self.toggle.clicked.connect(self.toggle_laser)

        # Gets a list of avaliable serial ports to connect and adds to combo box
        self.ports = serial_ports()
        for index, port in enumerate(self.ports):
            try:
                # Adds Classical/Quantum identifier based on HELP text
                dev = serial.Serial(port, baudrate=38400, timeout=0.1)
                time.sleep(2)
                dev.reset_input_buffer()
                dev.reset_output_buffer()
                dev.write("help ".encode())
                while True:
                    if dev.in_waiting:
                        response = dev.readlines()[0].decode().strip().split()[0]
                        self.ports[index] += " (" + response + ")"
                        break
                dev.close()
            except:
                pass
        self.deviceBox.addItems(self.ports)

        """
        # Initialise plots
        self.plotWidget.plotItem.getAxis('left').setPen((0,0,0))
        self.plotWidget.plotItem.getAxis('bottom').setPen((0,0,0))
        labelStyle = {'font': 'Arial', 'font-size': '16px'}
        self.plotWidget.setLabel('left', 'Power', 'V',**labelStyle)
        self.plotWidget.setLabel('bottom', 'Absolute Angle', '',**labelStyle)


        # Set timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(REFRESH_RATE)
        self.timer.start()
        """

        # Update status
        self.statusbar.showMessage("Ready to run ... Select your device!")
    """
    def initialiseParameters(self):

        # Data for plotting
        self.xdata = np.arange(-180+self.offset,181+self.offset,1)
        self.ydata = np.zeros(361)
        self.plot = self.plotWidget.plot(self.xdata, self.ydata, pen={'color':(255,0,0),'width':2})
        # Some cosmetics
        self.plotWidget.setLimits(xMin = self.xdata[0], xMax = self.xdata[-1])
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
            self.motor.power_off()
            self.statusbar.showMessage("Device Running")
            self.laserOn = False
            self.labelPower.setText("OFF")
            self.buttonStart.setText("Stop")

            #Initialising the motors
            self.curr_angle = float(self.motor.get_angle())
            self.offset  = int(self.motor.get_offset())
            print((self.offset))
            self.update_offset(self.offset)
            self.update_angle(self.curr_angle)
            self.deviceRunning = not self.deviceRunning
        else:
            if self.laserOn:
                self.toggle_laser()
            #Stop the device
            self.deviceRunning = not self.deviceRunning
            self.statusbar.showMessage("Device Stopped")
            # Change button appearance
            self.motor.close_port()
            self.buttonStart.setText("Start")

            if self.laserOn:
                self.toggle_laser()

    def toggle_laser(self):
        if self.laserOn:
            #now laser is on, turn off laser
            self.motor.power_off()
            self.labelPower.setText("OFF")
            self.laserOn = not self.laserOn

        else:
            #now laser if off, turn on laser
            self.motor.power_on()
            self.labelPower.setText("ON")
            self.laserOn = not self.laserOn

    def reset_params(self):
        #Resets the polarisation,angle and offset fields to zero
        self.statusbar.showMessage("Resetting Parameters... Please Wait")
        self.update_angle(0)
        self.update_offset(0)
        self.statusbar.showMessage("Resetting Parameters... Done")

    def set_angle_gui(self):
        #Set absolute angle
        abs_angle = self.angleInput.value()
        self.update_angle(abs_angle)
        return None

    def update_angle(self,angle_value):
        #Change the absolute angle in GUI and here
        self.statusbar.showMessage("Updating Angle... Please Wait")
        self.curr_angle = angle_value
        self.angleInput.setValue(angle_value) # QDoubleSpinBox - See guiSnd.ui file
        self.motor.set_angle(angle_value)
        self.statusbar.showMessage("Updating Angle... Done")

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

    def cleanUp(self):
        if self.laserOn:
            self.toggle_laser()

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
