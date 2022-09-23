# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 11:40:21 2022

@author: ryan.robinson
"""

import serial
import time

def main():
    """ For unit testing. """
    
    comport = 'COM11'
    RC = Relays(comport)
    
    try:
        for i in range(1,7):
            RC.switch(i)
            time.sleep(0.5)
    finally:
        RC.close()
        
    return
    
class Relays(serial.Serial):
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
    
    def switch(self, relay):
        """ Sends a command to the arduino to turn on/off relays.
        0 - Turn on all emitters
        1 - Turn on only emitter 1
        2 - Turn on only emitter 2
        3 - Turn on only emitter 3
        4 - Turn on only emitter 4
        5 - Turn on only emitter 5
        6 - Turn on only emitter 6
        """
        self.write('<{}>'.format(relay).encode()) # Write serial command
        return
    
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