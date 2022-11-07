# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 10:59:00 2022

@author: ryan.robinson

REQUIRES NI-VISA TO RUN:
    https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=PM100x

MAKE SURE PM101 IS SET TO USE NI-VISA DRIVERS, CAN CHANGE DRIVER IN THORLABS 
OPTICAL POWERMETER SOFTWARE:
    https://www.thorlabs.com/software_pages/viewsoftwarepage.cfm?code=OPM
    
SCPI LANGUAGE GUIDE FOR PM101:
    https://www.thorlabs.com/_sd.cfm?fileName=MTN013681-D04.pdf&partNumber=PM101
    
    NOTE:
        THE ABREVIATED SCPI COMMANDS DONT SEEM TO WORK. USE THE COMPLETE COMMANDS
"""
import time
import pyvisa

def main():
    """
    FOR UNIT TESTING
    """
    # LIST USB RESOURCES AVAILIBLE
    showResources()
    
    # DEVICE ADDRESS OF PM101
    addr = 'USB0::0x1313::0x8076::M00808684'
    
    try:
        print("Trying to connect...")
        PM = PowerMeter(addr, pprint = True)
        print("Connected")
        
        print("Getting ID...")
        PM.getIDN()
        
        print("Clearing status")
        PM.clearStatus()
        
        print("Setting wavelength to 450 nm")
        PM.setWL(450.0)
        
        PM.setBeamDia(50)
        time.sleep(0.2)
        print("Get beam dia")
        PM.getBeamDia()
        
        print("Getting set wavelenght...")
        PM.getWL()
        
        PM.setAvg(1000)
        print("Getting info")
        PM.getInfo()
        
        print("Getting power reading...")
        t = time.time()
        PM.getPower2()
        print(time.time() - t)
    finally:
        print("Closing...")
        PM.close()
    
    
    return

def showResources():
    """
    LIST AVAILIBLE USB DEVICES.
    """
    rm = pyvisa.ResourceManager()
    rm = rm.list_resources()
    print("Availible resources:")
    print(rm)
    return rm

class PowerMeter():
    def __init__(self, usbaddr = 'USB0::0x1313::0x8076::M00808684', pprint = False):
        """
        CONNECT TO THORLABS PM101.
        """
        # CREATE A USB DEVICE OBJECT
        self.pm = USBDevice(usbaddr)
        
        # PRINT COMMAND RESPONSES?
        self.pprint = pprint
        
        # Define pre-sets
        self.preSet()
        
        return
    
    def preSet(self):
        self.setBeamDia(dia = 50)
        self.setWL(450)
        self.setAvg(1000)
        
        return
    
    def getInfo(self):
        
        response = self.pm.send('SENSe:AVERage:COUNt?')
        
        print(response)
        
        return response
    
    def setBeamDia(self, dia = 50):
        
        command = "SENSe:CORRection:BEAMdiameter {}".format(dia)
        
        self.pm.write(command)
        
        return
    
    def getBeamDia(self):
        
        response = self.pm.send('SENSe:CORRection:BEAMdiameter?')
        
        print(response)
        
        return response
    
    def setAvg(self, num = 10):
        
        command = 'SENSe:AVERage:COUNt {}'.format(num)
    
        self.pm.write(command)
    
    def getIDN(self):
        """
        GET IDN OF PM101.
        """
        # SEND IDN AND GET RESPONSE
        response = self.pm.send('*IDN?')
        
        # PRINT RESPONSE
        if(self.pprint):
            print(response)        
        
        # RETURN RESPONSE
        return response
    
    def clearStatus(self):
        """
        CLEAR THE STATUS OF THE DEVICE.
        """
        # SEND COMMAND TO CLEAR STATUS OF THE DEVICE
        self.pm.write("*CLS")
    
        return
    
    def setWL(self, wl = 450.0):
        """
        SET THE WAVELENGTH OF THE POWERMETER.
        """
        # SEND IDN AND GET RESPONSE
        self.pm.write('SENSe:CORRection:WAVelength {}'.format(wl))
      
        return
    
    def getWL(self):
        """
        GET THE CURRENT SET WAVELENGTH OF THE POWERMETER.
        """
        # SEND IDN AND GET RESPONSE
        response = self.pm.send('SENSe:CORRection:WAVelength?')
        
        # PRINT RESPONSE
        if(self.pprint):
            print(response + " nm")        
        
        # RETURN RESPONSE
        return response
    
    def getPower(self):
        """
        GET THE POWER OF THE THERMOPILE.
        """
        # SEND CAMMAND TO RECIEVE POWER READING
        response = self.pm.send('SENSe:CORRection:POWer?')
        
        # PRINT RESPONSE
        if(self.pprint):
            print(response + " W")
        
        # RETURN RESPONSE
        return float(response)
    
    def getPower2(self):
        
        command = 'MEASure:SCALar:POWer?'
        response = self.pm.send(command)
        if(self.pprint):
            print(response + " W")
        
        return float(response)
    
    def close(self):
        """
        CLOSE THE DEVICE.
        """
        try:
            # SHUT OFF CURRENT OUTPUT
            if(self.pprint):
                print("shutting off")
        finally:
            # CLOSE THE DEVICE
            self.pm.close()
        
        return

# GENERIC USB DEVICE CLASS
# USED TO COMMUNICATE WITH THE THORLABS ITC40005    
class USBDevice:
    def __init__(self,rname):
        self.inst = pyvisa.ResourceManager().open_resource(rname)
        return None
    
    def settimeout(self,timeout):
        """
        Sets the timeout.

        Parameters
        ----------
        timeout : int
            time before an exception is thrown.

        Returns
        -------
        None.

        """
        self.inst.timeout = timeout+1000
        
        return
    
    def write(self,command):
        """
        Sends a command that requires no response. 

        Parameters
        ----------
        command : str
            command string.

        Returns
        -------
        None.

        """
        self.inst.write(command)
        
        return
    
    def send(self,command):
        """
        Sends a command that gives a response.

        Parameters
        ----------
        command : str
            command string.

        Returns
        -------
        str
            command response.

        """
        return self.inst.query(command).strip('\r\n')
    
    def close(self):
        """
        Closes the device.

        Returns
        -------
        None.

        """
        self.inst.close()
        
        return
    
    
if (__name__ == "__main__"):
    main()
    
