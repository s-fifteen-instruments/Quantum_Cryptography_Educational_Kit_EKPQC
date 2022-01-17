import S15lib.instruments.powermeter as pw
from S15lib.instruments import serial_connection as sc
import serial
import time
import datetime

path = 'COM5'
wavelength = 656
delay = 1
delay_scale = 1 # 1-second, 60-minute, 3600-hour.
angle = 135 # Angle to rotate polariser
file_name = '1214.csv'
timingfile_name = 'timing1.csv'

dev = pw.PowerMeter('COM5') # Power Meter
#ardu = serial.Serial(port = 'COM12', baudrate = 115200, timeout = 1) # Arduino
ardu = sc.SerialConnection(device_path= 'COM12', baud_rate=115200)

def one_call(cmd: str, wavelength):
    anglestr = cmd
    line1 = '' # To check if same angle is being called multiple times
    loopstart = time.time()
    while True:
        #print('Calling angle {}'.format(anglestr))
        loopstart = time.time()
        line = ardu.getresponse(anglestr, timeout = 10)
        # Arduino occasionally responds slow
        if line == '':
            print('Wait a little more...')
            time.sleep(10)
            continue
        print(line)
        try:
            mangle = line.split()[-1] # Motor Angle
            newangle = float(mangle) + angle + 1
            if newangle > 360:
                newangle -= 360
            anglestr = format(newangle, '.2f')
            pow = dev.get_power(wavelength)
            print(pow)
            with open(file_name, 'a+') as f:
                print('{},{}'.format(mangle, pow), file = f)
            line1 = line
            loopend = time.time()
            print('loop time: {}'.format(loopend-loopstart))
            with open(timingfile_name, 'a+') as f:
                print('{}'.format(loopend-loopstart), file = f)
        except:
            time.sleep(10)
            continue



print(one_call('10.00', 656))
