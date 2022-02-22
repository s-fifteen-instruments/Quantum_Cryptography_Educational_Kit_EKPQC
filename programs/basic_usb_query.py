import time
import serial

porto = 'COM7'

dev = serial.Serial(porto, baudrate=38400, timeout=0.1)

print("Opening the serial port...")
time.sleep(2) # Ports take longer to fully open on some systems.
print("Done\n")

# Flushing buffers
print("Flushing serial port")
dev.reset_input_buffer()
dev.reset_output_buffer()
print("Flushed")

dev.write("help ".encode())

while True:
    if dev.in_waiting:
        response = dev.readlines()[0].decode().strip().split()[0]
        print(response)
        break

dev.close()
print("Finished\n")
