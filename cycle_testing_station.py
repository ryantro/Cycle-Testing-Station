# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 13:30:47 2022

@author: ryan.robinson
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 11:05:00 2022

@author: ryan.robinson
"""

# IMPORTS
import tkinter as tk
from tkinter import ttk
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import os

# FOR UNIT TESTING
import random

# POWER METER
import power_meter

# SPECTRUM ANALYZER
import spectrum_analyzer

# STAGE CONTROL
import arduino

# Laser drivers
import current_supply

class DeviceAddrs:
     cs1 = 'COM3'
     cs2 = 'COM5'
     cs3 = 'COM8'
     cs4 = 'COM6'
     cs5 = 'COM7'
     osa = 'HR4D3341'
     ard = 'COM4'
     pm  = 'USB0::0x1313::0x8076::M00808684'

class Module_Positions:
    m1 = 475
    m2 = 6475
    m3 = 12515
    m4 = 18535
    m5 = 24555

class Application:
    def __init__(self, master):
        """ CREATE THE PROGRAM GUI """
        self.devices = DeviceAddrs()
        self.modules = Module_Positions()
        
        # APPLICATION MASTER FRAME
        self.master = master
        
        # ON APPLICAITON CLOSING
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # BOX CONFIGURE
        self.master.title('M.O.P.R. - Multi Optical Power Recorder')
        
        # DEFINE RUNFRAME
        self.runframe = tk.Frame(self.master)
        self.runframe.rowconfigure([0, 1, 2, 3], minsize=30, weight=1)
        self.runframe.columnconfigure([0, 1, 2], minsize=25, weight=1)

        # ENTRY LABEL
        self.entryLabel = tk.Label(self.runframe,text="Save folder:", font = ('Ariel 15'))
        self.entryLabel.grid(row=0, column=0, sticky = "W", padx = 10)
        
        # ENTRY BOX
        self.entry = tk.Entry(self.runframe, text = 'Entry', width = 60, font = ('Ariel 15'))
        self.entry.grid(row = 0, column = 1, sticky = "W", padx = (0,10), pady = 10)
        self.entry.insert(0, r'record-folder')

        # CHECK BOX
        self.saveVar = tk.BooleanVar()
        self.saveVar.set(False)
        self.saveBox = tk.Checkbutton(self.runframe, text='Save To CSV', variable = self.saveVar, onvalue = True, offvalue = False, font = ('Ariel 10'))
        self.saveBox.grid(row = 0, column = 2, sticky = "E", padx = 10)

        # GENERATE STATION ENABLE BOX
        self.stateframe = tk.Frame(self.runframe, borderwidth = 2,relief="groove")
        self.stateframe.columnconfigure([0, 1], minsize=50, weight=1)
        self.stateframe.rowconfigure([0], minsize=50, weight=1)
        self.stateframe.grid(row = 3, column = 0, columnspan = 3, padx = 10, pady = (0,10), sticky = "EW")
        
        # GENERATE ENABLE/DISABLE BUTTON
        self.stateButton = tk.Button(self.stateframe, text="START", command=self.stateEnable, font = ('Ariel 15'))
        self.stateButton.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = "NSEW")
        
        # GENERATE STATION STATUS BOX
        self.statelabel = tk.Label(self.stateframe, text=" RECORDING OFF ", bg = '#84e47e', font = ('Ariel 15'))
        self.statelabel.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "NSEW")

        # VARIABLES
        self.recording = False
        self.tList = []
        self.pList = []
        
        # LASER MODULES
        self.mFrames = tk.Frame(self.runframe)
        self.mFrames.columnconfigure([0, 1, 2, 3, 4], minsize=10, weight=1)
        self.mFrames.grid(row = 2, column = 0, columnspan = 3, padx = 5, pady = (0,10), sticky = "EW")
        
        """ Create laser modules """
        self.Ms = []
        for i in range(0,5):
            self.Ms.append(LaserModule(self.mFrames, i))
        
        # THREADS
        self.recordThread = threading.Thread(target = self.record)
        
        # FRAME PACKING
        self.runframe.pack()
        
        # CONNECT AND ATTACH DEVICES
        self.connectDevices()
        return
    
    
    def connectDevices(self):
        
        # CONNECT STAGE
        self.stage = arduino.Stage(self.devices.ard)
        
        # CONNECT POWER METER
        self.pm = power_meter.PowerMeter(usbaddr = self.devices.pm)
        
        # CONNECT TO OSA
        self.osa = spectrum_analyzer.SpectrumAnalyzer()
        self.osa.connect(integration_time = 1500, serialnum = self.devices.osa)
        
        # CONNECT LASER DRIVERS
        self.ld1 = current_supply.PS2000B(self.devices.cs1)
        self.ld2 = current_supply.PS2000B(self.devices.cs2)
        self.ld3 = current_supply.PS2000B(self.devices.cs3)
        self.ld4 = current_supply.PS2000B(self.devices.cs4)
        self.ld5 = current_supply.PS2000B(self.devices.cs5)
        
        # Create laser driver list
        self.lds = [self.ld1, self.ld2, self.ld3, self.ld4, self.ld5]

        # Configure laser drivers
        for ld in self.lds:
            ld.enable_remote_control()
            ld.set_current(0)
            ld.enable_output()
             
        # ZERO STAGE
        self.stage.zero()
        
        # Set postions of modules
        self.Ms[0].setPos(self.modules.m1)
        self.Ms[1].setPos(self.modules.m2)
        self.Ms[2].setPos(self.modules.m3)
        self.Ms[3].setPos(self.modules.m4)
        self.Ms[4].setPos(self.modules.m5)
        
        # Attach lasers drivers to modules
        self.Ms[0].connectLD(self.ld1)
        self.Ms[1].connectLD(self.ld2)
        self.Ms[2].connectLD(self.ld3)
        self.Ms[3].connectLD(self.ld4)
        self.Ms[4].connectLD(self.ld5)
        
        # Attach instruments to modules
        for M in self.Ms:
            M.devices.connectPM(self.pm)
            M.devices.connectOSA(self.osa)
            M.devices.connectStage(self.stage)
        
        return
    
    def closeDevices(self):
        
        for ld in self.lds:
            ld.set_current(0)
            ld.disable_output()
            ld.close()
        
        self.stage.close()
        self.pm.close()
        self.osa.close()
        return
    
    
    def stateEnable(self):
        """ ENABLE THE STATE """
            
        # DISABLE ENTRY BOX
        self.entry.configure(state = 'disabled')
        
        # CONFIGURE BUTTON
        self.stateButton = tk.Button(self.stateframe, text="STOP", command=self.stateDisable, font = ('Ariel 15'))
        self.stateButton.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "NSEW")
        
        # CONFIGURE LABEL
        self.statelabel = tk.Label(self.stateframe, text = "CURRENTLY RECORDING", bg = '#F55e65', font = ('Ariel 15'))
        self.statelabel.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = "NSEW")    
        
        # SET RECORDING STATE TO TRUE
        self.recording = True
        
        # START THE THREAD IF IT CURRENTLY ISN'T ALIVE
        if(self.recordThread.is_alive() == False):
            
            # CREATE THE THREAD
            self.recordThread = threading.Thread(target = self.record)
            
            # START THE THREAD
            self.recordThread.start()
                
        return
    
    def stateDisable(self):
        """ DISABLE THE STATE """
        
        # SET RECORDING STATE TO FALSE
        self.recording = False
        
        # ENABLE ENTRY BOX
        self.entry.configure(state = 'normal')
        
        # CONFIGURE STATE BUTTON
        self.stateButton = tk.Button(self.stateframe, text="START", command=self.stateEnable, font = ('Ariel 15'))
        self.stateButton.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = "NSEW")
        
        # CONFIGURE STATE LABEL
        self.statelabel = tk.Label(self.stateframe, text=" RECORDING OFF ", bg = '#84e47e', font = ('Ariel 15'))
        self.statelabel.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "NSEW")

        # CLOSE THE THREAD IF IT IS CURRENTLY ALIVE
        while(self.recordThread.is_alive() == True):
            
            # CREATE THE THREAD
            print("Waiting for thread to finish...")
            time.sleep(2)

        return

    """FOR TESTING"""
    def record(self):
        # RECORD DATA WHILE RECORDING
        self.cycled = False
        
        # Turn lasers on!!!
        for M in self.Ms:
            print("L")
        
        while(self.recording):
            
            for M in self.Ms:
                if(M.enabled):
                    
                    """ turn on lasers """
                    if(self.cycled):
                        t1 = time.time()
                        for M in self.Ms:
                            print("Lazas on")
                    
                    M.measure()
                    
                    """ time laser was on """
                    if(self.cycled):
                        ton = time.time() - t1
                        if(ton < 20):
                            time.sleep(20-ton)
                    
                    
                    """ turn lasers off """
                    if(self.cycled):
                        for M in self.Ms:
                            print("Lazas off")
                        time.sleep(20)
                    
                    
                    #time
            
            # SLEEP
            time.sleep(1)
            
        # TURN LASERS OFF !!!
        for M in self.Ms:
            print("Lazas off")
        
        return
    
    def on_closing(self):
        """ EXIT THE APPLICATION """
        
        # PROMPT DIALOG BOX
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            
            
            
            self.stateDisable()
            
            self.closeDevices()
            
            # SET RECORDING TO FALSE
            # self.recording = False
            
            # # JOIN THE THREAD IF IT IS ALIVE
            # if(self.recordThread.is_alive() == True):
            #     self.recordThread.join(2)
            
            # DESTROY APPLICATION
            self.master.destroy()
            
        return

class Devices:
    stage = None
    pm = None
    osa = None
    ld = None
    
    def connectStage(self, stage):
        self.stage = stage
        return
    
    def connectPM(self, pm):
        self.pm = pm
        return
    
    def connectOSA(self, osa):
        self.osa = osa
        return
    
    def connectLD(self, ld):
        self.ld = ld
        return

    def checkConnected(self):
        if(self.stage == None or self.pm == None or self.osa == None or self.ld == None):
            return False
        else:
            return True

class Values:
    power = 0
    wl = 0
    lw = 0
    sk = 0
    kt = 0
    
    def reset(self):
        self.power = 0
        self.wl = 0
        self.lw = 0
        self.sk = 0
        self.kt = 0
        return
        
    def save(self, title):
        """ Save file """
        t = time.time()
        saveline = "{}, {}, {}, {}, {}, {}\n".format(t, self.power, self.wl, self.lw, self.sk, self.kt)
        os.makedirs(os.path.dirname(title), exist_ok=True)
        with open(title, 'a') as file_obj:
            file_obj.write(saveline)
        return

class LaserModule:
    def __init__(self, master, g):
        """
        CREATE AN OBJECT FOR A LASER MODULE
        """
        # DEFINE MODULE FRAME
        self.master = tk.Frame(master)
        self.master.rowconfigure([0, 1, 2, 3, 4, 5, 6], minsize=5, weight=1)
        self.master.columnconfigure([0], minsize=5, weight=1)
        self.master.grid(row = 0, column = g)
        
        # MODULE LABEL
        self.moduleLabel = tk.Label(self.master, text = "Module-{}".format(g), font = ('Ariel 15'))
        self.moduleLabel.grid(row = 0, column = 0, sticky = "W", padx = 5)
        
        # ENTRY BOX
        self.moduleFrame = tk.Entry(self.master, text = 'Entry {}'.format(g), width = 10, font = ('Ariel 15'))
        self.moduleFrame.grid(row = 1, column = 0, sticky = "EW", padx = 5)
        self.moduleFrame.insert(0, r'1001234')
        
        # MOST RECENT POWER MEASUREMENT
        pStr = "Power: {:.4f} W".format(0)
        self.pVar = tk.StringVar(self.master, value = pStr)
        self.pM = tk.Label(self.master, textvariable = self.pVar, font = ('Ariel 8'))
        self.pM.grid(row=2, column=0, sticky = "w", padx = 5)
        
        # MOST RECENT SPECTRUM MEASUREMENT
        sStr = "Center WL: {:.4f} nm".format(0)
        self.sVar = tk.StringVar(self.master, value = sStr)
        self.sM = tk.Label(self.master, textvariable = self.sVar, font = ('Ariel 8'))
        self.sM.grid(row=3, column=0, sticky = "w", padx = 5)
        
        # STATUS BOX
        self.statusVar = tk.StringVar(self.master, value = "Status: Not started")
        self.statusLabel = tk.Label(self.master, textvariable = self.statusVar, font = ('Ariel 8'))
        self.statusLabel.grid(row = 4, column = 0, sticky = "W", padx = 5)
        
        # ENABLE DISABLE BOX
        self.stateframe = tk.Frame(self.master, borderwidth = 2,relief="groove")
        self.stateframe.columnconfigure([0, 1], minsize=120, weight=1)
        self.stateframe.rowconfigure([0], minsize=5, weight=1)
        self.stateframe.grid(row = 5, column = 0, columnspan = 3, padx = 5, sticky = "EW")
        
        # MEASURE BUTTON
        self.measureButton = tk.Button(self.master, text="MEASURE", command=self.measureSingle, font = ('Ariel 8'))
        self.measureButton.grid(row = 6, column = 0, columnspan = 3, padx = 5, sticky = "EW")
        
        # STATE
        self.enabled = True
        
        # ENABLE DEVICE
        self.enable()
        
        # Is diode in safe region?
        self.dangerZone = False
        self.maxPower = 0.0
        self.currentPower = 0.0
        
        # Position
        self.pos = 0
        self.specOffSet = 7080
        
        # Create a devices object
        self.devices = Devices()
        
        # Create a values object
        self.values = Values()
        
        # time of state change
        self.tStateChange = time.time()
        return
    
    def setPos(self, pos):
        self.pos = pos
        return
    
    def turnOn(self):
        """ Turn the laser on """
        if(self.enabled):
            self.tStateChange = time.time()
            current = 2.8
            self.devices.ld.set_current(current)
        return
    
    def turnOff(self):
        """ Turn the laser off """
        self.tStateChange = time.time()
        self.devices.ld.set_current(0)
        return
    
    def measureSingle(self):
        self.devices.ld.set_current(2.8)
        self.measure()
        self.devices.ld.set_current(0)
    
    def measure(self):
        """ Measure the power and wavelength """
        if(self.enabled):
            tsleep = 10
            
            if(self.devices.stage == None):
                return
            
            self.devices.stage.move(self.pos)
            
            print('sleeping {} seconds before measuring power...'.format(tsleep))
            time.sleep(tsleep)
            
            # Record power
            self.devices.recordPower()
            
            # Move osa to module
            self.devices.stage.relmove(self.specOffSet)
            
            # Record spectrum
            self.devices.recordSpectrum()
            
            # Save data
            filename = self.moduleFrame.get()
            self.values.save('test-data/{}.csv'.format(filename))
            
        
        return
    
    def recordPower(self):
        """
        RECORD THE POWER
        """
        if(self.enabled == False):
            return
        
        # Record power
        self.values.power = self.devices.pm.getPower2()
        
        # Update gui
        pStr = "Power: {:.4f} W".format(self.values.power)
        self.pVar.set(pStr)
        
        return
    
    def recordSpectrum(self):
        """
        RECORD THE SPECTRUM
        """
        if(self.enabled == False):
            return
        
        # Take a spectrum
        self.devices.osa.measureSpectrum()
        
        # Get the statistics
        results = self.devices.osa.findStatistics()
        
        # Find the mean wavelength
        self.values.wl = results[0]
        
        # Find the weighted standard deviation
        self.values.lw = results[1]
        
        # Update the gui
        sStr = "Center WL: {:.4f} nm".format(self.values.wl)
        self.sVar.set(sStr)
        
        return
    
    def enable(self):
        """
        SET ENABLED STATE TO TRUE
        """
        # SET ENABLED STATE TO TRUE
        self.enabled = True
        
        # GENERATE ENABLE/DISABLE BUTTON
        self.stateButton = tk.Button(self.stateframe, text="DISABLE", command=self.disable, font = ('Ariel 8'))
        self.stateButton.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "NSEW")
        
        # GENERATE STATION STATUS BOX
        self.statelabel = tk.Label(self.stateframe, text=" MODULE ENABLED ", bg = '#F55e65', font = ('Ariel 8'))
        self.statelabel.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = "NSEW")
        
        # MEASUREBUTTON
        self.measureButton.configure(state = 'normal')
        return
    
    def disable(self):
        """
        SET ENABLED STATE TO FALSE
        """
        # SET ENABLED STATE TO FALSE
        self.enabled = False
        
        # GENERATE ENABLE/DISABLE BUTTON
        self.stateButton = tk.Button(self.stateframe, text="ENABLE", command=self.enable, font = ('Ariel 8'))
        self.stateButton.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = "NSEW")
        
        # GENERATE STATION STATUS BOX
        self.statelabel = tk.Label(self.stateframe, text=" MODULE DISABLED ", bg = '#84e47e', font = ('Ariel 8'))
        self.statelabel.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "NSEW")
        
        # MEASURE BUTTON
        self.measureButton.configure(state = 'disabled')
        return

def main():
    """ MAIN THREAD """
    # CREATE ROOT TKINTER OBJECT
    root = tk.Tk()
    
    # CREATE APPLICATION
    app = Application(root)
    
    # RUN MAINLOOP
    root.mainloop()
    
    return


if __name__=="__main__":
    main()