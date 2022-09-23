
# Python code transmits a byte to Arduino /Microcontroller

import serial

import time

SerialObj = serial.Serial('COM10') # COMxx   format on Windows
                                   # ttyUSBx format on Linux

SerialObj.baudrate = 9600  # set Baud rate to 9600
SerialObj.bytesize = 8     # Number of data bits = 8
SerialObj.parity   ='N'    # No parity
SerialObj.stopbits = 1     # Number of Stop bits = 1

time.sleep(3)

print('Moving...')
SerialObj.write(b'<MOVEREL 1000>')      #transmit 'A' (8bit) to micro/Arduino
a = SerialObj.readline()
print(a)
print("DONE 1!")

time.sleep(1)

SerialObj.write(b'<ZERO>')
a = SerialObj.readline()
print(a)
print("DONE 2!")

time.sleep(1)

SerialObj.write(b'<MOVEABS 10000>')
a = SerialObj.readline()
print(a)
print("DONE 3!")

time.sleep(1)

SerialObj.write(b'<MOVEABS 20000>')      
a = SerialObj.readline()
print(a)
print("DONE 4!")

time.sleep(1)

SerialObj.write(b'<MOVEABS 30000>')  
a = SerialObj.readline()
print(a)
print("DONE 5!")

time.sleep(1)

SerialObj.write(b'<MOVEABS 0>')  
a = SerialObj.readline()
print(a)
print("DONE 6!")

SerialObj.close()          # Close the port