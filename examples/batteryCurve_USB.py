"""This sample program will use the kel103 to test a batteries capacity and 
show this information in matplotlib. This method is an aproximation and its resolution
can be increase with sampling rate. 
"""
import socket
import time
import re
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import sys
import os
# Add the korad directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from korad.kel103_usb import kel103


#test proporties
cutOffVoltage = 3
dischargeRate = 0.45
MISSED_LIMIT = 10 # amount of missed samples that is allowed

# setup the device (the IP of your ethernet/wifi interface, the IP of the Korad device)
device = kel103('COM7', 115200)
device.checkDevice()

# a quick battery test
device.setOutput(False)        
voltage = device.measureVolt()
device.setCurrent(dischargeRate)
voltageData = []
timeData = []
current = 0
capacity = 0
device.setOutput(True)

# run the test
startTime = time.time()
current_time = startTime
missedSuccessiveSamples = 0

while voltage > cutOffVoltage:
    try:
        # store the time before measuring volt/current
        voltage = device.measureVolt()
        current = device.measureCurrent()
        voltageData.append(voltage)
        # Only append the timedata when volt/current measurements went fine.
        # This is because the voltage or current measurement could fail
        # and then the x and y-axis would have different dimentions
        previous_time = current_time
        current_time = time.time()
        timeData.append(time.time() - startTime)

        # solve the current stuff as a running accumulation
        # capacity += ((previous_time - current_time) / 60 / 60) * current
        capacity += ((current_time - previous_time) / 60 / 60) * current * 1000

        print("Voltage: " + str(voltage) + " V DC, Capacity: " + str(capacity) + " mAh, Discharge Rate: " + str(dischargeRate) + " A")
        time.sleep(0.25)
        missedSuccessiveSamples = 0
    except Exception as e:
        print(e)
        missedSuccessiveSamples += 1
        if missedSuccessiveSamples >= MISSED_LIMIT:
            raise Exception("Too many missed samples!")

# disable the output
device.setOutput(False)
device.endComm()

# plot the finished data
fig, ax = plt.subplots()
ax.plot(timeData, voltageData)

ax.set(xlabel='time (s)', ylabel='voltage (V DC)',
    title='Battery Discharge Test {}A: {:.4f}mAh'.format(dischargeRate, capacity))
ax.grid()

fig.savefig("test_" + str(time.time()) + ".png")
plt.show()
