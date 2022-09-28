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

# FOR UNIT TESTING
import random

# POWER METER
import power_meter

# SPECTRUM ANALYZER
import spectrum_analyzer

# STAGE CONTROL
import arduino

class Application:
    def __init__(self, master):
        """ CREATE THE PROGRAM GUI """
        
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
        
        self.Ms = []
        for i in range(0,5):
            self.Ms.append(LaserModule(self.mFrames, i))
        
        # THREADS
        self.recordThread = threading.Thread(target = self.record)
        
        # FRAME PACKING
        self.runframe.pack()
        
        self.connectDevices()
        return
    
    
    def connectDevices(self, arduinoCom = 'COM10', pmcom = '', sacom = ''):
        self.stage = arduino.Stage('COM10')
        self.stage.zero()
        
        pos = 5000
        for M in self.Ms:
            M.attachStage(pos, self.stage)
            pos = pos + 5000
        
        return
    
    def closeDevices(self):
        self.stage.close()
        
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
        if(self.recordThread.is_alive() == True):
            
            # CREATE THE THREAD
            self.recordThread.join(10000) # timeout of 10 seconds

        return

    """FOR TESTING"""
    def record(self):
        # RECORD DATA WHILE RECORDING
        while(self.recording):
            
            for M in self.Ms:
                if(M.enabled):
                    M.recordPower()
                    M.recordSpectrum()
            
            # SLEEP
            time.sleep(1)

    def record2(self):
        """ RECORD DATA FROM THE POWER METER """
        
        try:
            # CONNECT TO POWER METER DEVICE
            PM = power_meter.PowerMeter()
        
            # CLEAR LISTS
            self.tList = []
            self.pList = []
            
            # CONFIGURE PLOT
            self.powerPlot.cla()
            self.powerPlot.set_title("Power")
            self.powerPlot.set_ylabel("Power (mW)", fontsize = 14)
            self.powerPlot.set_xlabel("Time (s)", fontsize = 14)
            self.powerPlot.grid('On')
            
            # MARK START TIME
            startTime = time.time()
            
            # RECORD DATA WHILE RECORDING
            while(self.recording):
                
                # UPDATE THE MOST RECENT VALUE
                recentVal = PM.getPower2()
                self.var.set("Power: {:.4f} mW".format(recentVal))
                
                # APPEND VALUES TO LISTS
                self.tList.append(time.time())
                self.pList.append(recentVal)
                
                # UPDATE THE PLOTS
                if(len(self.tList) > 1):
                    self.powerPlot.plot([self.tList[-2] - startTime, self.tList[-1] - startTime], [self.pList[-2], self.pList[-1]], color = 'orange') #self.tList, self.pList)
                
                # UPDATE CANVAS
                self.canvas.draw_idle()
                
                if(self.saveVar.get()):
                    print("Saving")
                    with open(self.entry.get(), 'a') as f:
                        # WRITE VALUES TO FILES
                        f.write("{}, {}\n".format(self.tList[-1], self.pList[-1]))
                    
                # SLEEP
                time.sleep(1)
        
        finally:
            self.closeDevices()
            # CLOSE DEVICE
            PM.close()
        
        return
    
    def on_closing(self):
        """ EXIT THE APPLICATION """
        
        # PROMPT DIALOG BOX
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            
            self.stateDisable()
            
            # SET RECORDING TO FALSE
            # self.recording = False
            
            # # JOIN THE THREAD IF IT IS ALIVE
            # if(self.recordThread.is_alive() == True):
            #     self.recordThread.join(2)
            
            # DESTROY APPLICATION
            self.master.destroy()
            
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
        self.measureButton = tk.Button(self.master, text="MEASURE", command=self.measure, font = ('Ariel 8'))
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
        self.specOffSet= 4000
        
        # Stage
        self.stage = None
        return
    
    def attachStage(self, pos, stage):
        self.pos = pos
        self.stage = stage
        return
    
    def measure(self):
        print("Measure clicked")
        
        if(self.stage == None):
            return
        
        self.stage.move(self.pos)
        
        return
    
    def recordPower(self):
        """
        RECORD THE POWER
        """
        if(self.enabled == False):
            return
        
        # UNIT TEST
        power = 24.0
        
        # UPDATE POWER ON THE GUI
        self.updatePower(power)
        
        return
    
    def recordSpectrum(self):
        """
        RECORD THE SPECTRUM
        """
        if(self.enabled == False):
            return
        
        
        wl = 450.0
        
        # UPDATE SPECTRUM ON THE GUI
        self.updateWl(wl)
        
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
    
    def updatePower(self, power):
        """
        UPDATE THE POWER OF THE GUI
        """
        
        pStr = "Power: {:.4f} W".format(power)
        self.pVar.set(pStr)
        
        return
    
    def updateWl(self, wl):
        """
        UPDATE THE WAVELENGTH OF THE GUI
        """
        
        sStr = "Center WL: {:.4f} nm".format(wl)
        self.sVar.set(sStr)
        
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