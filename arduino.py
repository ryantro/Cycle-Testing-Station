# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 11:40:21 2022

@author: ryan.robinson
"""

import serial
import time

def main():
    """ For unit testing. """
    
    comport = 'COM10'
    S = Stage(comport)
    
    try:
        S.relmove(2000)
        time.sleep(1)
        S.move(10000)
        time.sleep(1)
        S.zero()
        print("test")
    finally:
        S.close()
    return
    
class Stage(serial.Serial):
    """ Class for controlling an arduino running the SETS firmware. """
    def __init__(self, comport):
        """ Initialization for the class, requires the comport. """
        super().__init__(comport)
        self.baudrate = 9600  # Set Baud rate to 9600
        self.bytesize = 8     # Number of data bits = 8
        self.parity   ='N'    # No parity
        self.stopbits = 1     # Number of Stop bits = 1
        time.sleep(3)         # Sleep 3 seconds for serial initilization
        return
    
    def move(self, pos):
        """ Sends a command to move the stage to a coordinate """
        print("Moving stage to coordinate: {}".format(pos))
        self.write('<MOVEABS {}>'.format(pos).encode()) # Write serial command
        return self.readline()
    
    def relmove(self, relpos):
        """ Sends a command to move the stage by a relative movement """
        print("Moving stage by relative amount: {}".format(relpos))
        self.write('<MOVEREL {}>'.format(relpos).encode()) # Write serial command
        return self.readline()
    
    def zero(self):
        """ Sends a command to zero the stage """
        print("Zero'ing the stage.")
        self.write('<ZERO>'.encode()) # Write serial command
        return self.readline()
    
    def close(self):
        """ Close the com port. """
        try:
            super().close()
        except Exception as e:
            self.setError("error closing port: {0}".format(e))
        except:
            self.setError("error closing port")
        return
    
if __name__=="__main__":
    main()