# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 11:51:49 2022

@author: ryan.robinson
"""
import math
import numpy, os
import matplotlib.pyplot as plt

# FOR OCEAN OPTICS HR4000
from seabreeze.spectrometers import Spectrometer, list_devices


def main():
    # filename = 'tests/dc-99.csv'
    
    # A = SpectrumAnalyzer()
    # A.loadData(filename)
    # a, b = A.findStatistics()
    # print(a)
    # print(b)
    # A.plotSpectrum()
    
    A = SpectrumAnalyzer()
    A.listDevices()
    A.connect()
    
    A.measureSpectrum()
    A.plotSpectrum()
    
    results = A.findStatistics()
    
    print(results[0])
    
    return

class SpecStats:
    mean = 0
    sdev = 0
    skew = 0
    kurt = 0
    
    def calcState(self, x, yf):
        self.x = x
        self.yf = yf
        self.getMean()
        self.getSdev()
        self.getSkew()
        self.getKurt()
        return
        
    def getMean(self):
        self.mean = numpy.dot(self.x, self.yf)
        return
    
    def getSdev(self):
        n = 2
        moment = numpy.dot((self.x - self.mean)**n, self.yf)
        self.sdev = math.sqrt(abs(moment))
        return

    def getSkew(self):
        n = 3
        moment = numpy.dot((self.x - self.mean)**n, self.yf)
        self.skew = moment / (self.sdev**n)
        return

    def getKurt(self):
        n = 4
        moment = numpy.dot((self.x - self.mean)**n, self.yf)
        self.kurt = moment / (self.sdev**n)
        return

# CONTROLS THE OCEAN OPTICS HR4000 OSA
# REQUIRES SEABREEZE TO BE INSTALLED
class SpectrumAnalyzer():
    def __init__(self):
        """
        Connect to Ocean Optics HR4000.
        Generate wavelength axis.

        Returns
        -------
        None.

        """
        return
    
    def listDevices(self):
        devices = list_devices()
        print(devices)
        return
    
    def connect(self, integration_time = 1500, serialnum = "HR4D3341"):
        """
        Connect to device
        """
        # SET OSA INTEGRATION TIME
        self.integration_time = integration_time
        
        # SET OSA DEVICE
        # SERIAL NUMBER: HR4D1482
        self.spec = Spectrometer.from_serial_number(serialnum)
        
        self.spec.integration_time_micros(self.integration_time)
        
        # GET WAVELENGTH X AXIS
        self.wavelengths = self.spec.wavelengths()
        
        return
    
    def loadData(self, filename):
        """
        Load file to class, this is mainly used for unit testing.
        """
        loadedData = numpy.genfromtxt(filename, delimiter = ',')
        self.wavelengths = loadedData[:,0]
        self.intensities = loadedData[:,1]
        
        return
    
    def close(self):
        """
        Close the device.

        Returns
        -------
        None.

        """
        try:
            self.spec.close()
        except Exception as e:
            print(e)
        
        return
    
    def findStatistics(self):
        """
        Finds the weighted mean and standard deviation of the data.

        Returns
        -------
        wmean : float
            weighted mean.
        sdev : float
            standard deviation.

        """
        # Subtract the noise floor
        tmp_int = self.intensities - min(self.intensities)
        
        tmp_int = tmp_int/numpy.sum(tmp_int)
        
        # Set the max filter level
        filterlv = 0.0015
        
        # Zero values unter the filterlv
        for i in range(0,len(tmp_int)):
            if(tmp_int[i] < filterlv):
                tmp_int[i] = 0
        
        tmp_int = tmp_int/numpy.sum(tmp_int)
        
        # plt.figure(2)
        # plt.plot(tmp_int)
        
        stats = SpecStats()
        stats.calcState(self.wavelengths, tmp_int)

        return stats.mean, stats.sdev, stats.skew, stats.kurt
    
    def measureSpectrum(self):
        """
        Measure data from the OSA.

        Returns
        -------
        None.

        """
        # READ INTENSITIES
        self.intensities = self.spec.intensities()
        
        return
    
    def getData(self):
        """
        Get the data in the buffer.

        Returns
        -------
        numpy array
            wavelength data.
        numpy array
            intensity data.

        """
        return self.wavelengths, self.intensities
    
    def plotSpectrum(self,title = ""):
        plt.plot(self.wavelengths,self.intensities)
        plt.xlim([435,455])
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Intensity")
        plt.grid("On")
        plt.title(title)
        plt.pause(0.05)
        return
    
    def saveWavelengthData(self, filename):
        """
        Save the wavelength data to a csv.

        Parameters
        ----------
        filename : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # Create directories for file
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Save data
        numpy.savetxt(filename, self.wavelengths, delimiter = ",")
        
        return
    
    def saveIntensityData(self, filename):
        """
        Save the intensity data to a csv

        Parameters
        ----------
        filename : str
            filename and foulders to save data in.

        Returns
        -------
        None.

        """
        # Create directories for file
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Generate save data
        savedata = numpy.column_stack((self.wavelengths,self.intensities))
        
        # Save data
        numpy.savetxt(filename, savedata, delimiter = ",")
        
        return

if __name__=="__main__":
    main()