# Sensor Fusion using Marzullo's Algorithm
#
# Current Functionality:
# Takes in readings from each of the 3 sets of sensors using the MUX channels
# Outputs the results to the screen
# Using the known precision, creates pairs at the outer bounds of the precision
## for each reading to make a range of precision.
# Passes the Previous Range Pairs to a function that performs Marzullo's
## Algorithm and prints out the resulting 'improved' precision result.
# New Precision is now also printed (found by taking the difference between the
## upper and lower bound of the new range and dividing in half)
# Writes Date, Time, Temp, and Humidity Readings to CSV file. Currently
## appends each new set of values to the next line of the CSV file.
## A new log file is created each day.
# If humidity has an absolute change of greater than 10% per hour, Alert is
## triggered.
# Alert is produced if current light exposure is greater than 200 lux
# Alert is produced if daily light exposure greater than 1000 lux hours
# Debug Mode implemented: If debug set to 1, print states will execute to aid in
## debugging.
# Alert is produced when a sensor, or multiple sensors fail
# Alert is produced when a specific sensor remains down for 3 cycles
#
# Questions:
# How often should readings be taken and should the 'loop' take place in this
## script or should another script run the loop and call this one within it?
# Should the code that triggers the LEDs based on the current readings be
## in a seperate script or should everything be in this script?
# For the result from Marzullo's Algorithm, should the range remain, or should
## the median value be taken?

import time
import qwiic
import board
import adafruit_htu31d
import adafruit_ltr390
import csv
import os
from datetime import datetime


#The name of this device
_DEFAULT_NAME = "Qwiic Mux"
_AVAILABLE_I2C_ADDRESS = [*range(0x70,0x77 + 1)]

# Sets Debug Mode (1 = On)
debug = 1

# Value to hold Cumulative Lux Hours over 24hr Period
luxHRs = 0

# Loop Counter
count = 0

## Increments when sensor is down, triggers LED at 3
ltr_down = 0
htu_down = 0

# List for Humidity Values over hour period to check for >10% change
## 1 reading per minute = 60 readings per hour
hum_over_hour = [None] * 60

# Instantiates an object for the MUX
test = qwiic.QwiicTCA9548A()

# Runs Marzullo's Algorithm on a set of data pairs
# Returns the smallest interval consistent with largest number of sources
## intervals = The set of data pairs passed to the function
## N = The number of pairs sent (The length)
## t = The type of data, used for formatting the output
def marzulloAlgorithm(intervals,N,t):
    l = intervals[0][0]
    r = intervals[0][1]

    for i in range(1,N):
        if (intervals[i][0] > r or intervals[i][1] < l):
            continue
        else:
            l = max(l, intervals[i][0])
            r = min(r, intervals[i][1])
    if debug == 1:
        if (t == 0):
            print("[%0.1f" % l,", %0.1f" % r,"]")
        elif (t == 1):
            print("[%0.1f%%" % l,", %0.1f%%" % r,"]")
        else:
            print("[",l,", ",r,"]")

    return l, r

# Writes data to a CSV log file. If file doesn't exist a new one is created
## dataList = data to append to next line of CSV log file
def logWrite(dataList):
    dateTimeObj = datetime.now()
    dateObj = dateTimeObj.date()
    currentDate = dateObj.strftime("%b-%d-%Y")
    file = "sensor_log_"+currentDate+".csv"
    headers = ['Date', 'Time Stamp', 'Temperature', 'Relative Humidity', 'Current Lux', 'Cumulative Lux Hours']

    # Checking if Log file exists
    if not os.path.exists(file):
        if debug == 1:
            print("Creating "+file)

        # creating file and adding column headers
        with open(file, 'w') as csvfile:
            # creating the csv writer object
            csvwriter = csv.writer(csvfile)
            # writing the column headers
            csvwriter.writerow(headers)
            # close the csv file
            csvfile.close()

    # appending new row to log file
    with open(file, 'a') as csvfile:
        # creating the csv writer object
        csvwriter = csv.writer(csvfile)
        # writing the data row
        csvwriter.writerow(dataList)
        # close csv file
        csvfile.close()

# Function to handle i2c communication and read in data from Sensors
# MUX channel is enabled, Data is read from the sensors then returned, MUX channel is disabled
## chan = the MUX channel to enable/disable and read in sensor data from
def readSensors(chan):
    # Enable MUX channel 'chan' to read the set of sensors
    test.enable_channels(chan)
    # Read the data from the LTR390 and HTU31D sensors
    i2c = board.I2C()
    ## 1 = sensor is up, 0 = sensor is down
    ltr_status = 0
    htu_status = 0

    try:
        if debug == 1:
            print("Checking LTR Sensor")
        ltr = adafruit_ltr390.LTR390(i2c)
        ltr_status = 1
    except ValueError as error1:
        print(error1)
        global ltr_down
        ltr_down = ltr_down + 1
        if debug == 1:
            print("LTR Sensor Down")

    try:
        if debug == 1:
            print("Checking HTU Sensor")
        htu = adafruit_htu31d.HTU31D(i2c)
        htu_status = 1
    except ValueError as error2:
        print(error2)
        global htu_down
        htu_down = htu_down + 1
        if debug == 1:
            print("HTU Sensor Down")

    if debug == 1:
        print("\nSensor Series has the following readings: ")
    if htu_status == 1:
        temperature, relative_humidity = htu.measurements
        if debug == 1:
            # Print Temp & Humidity Sensor Readings for Debugging Purposes
            print("Temperature: %0.1f C" % temperature)
            print("Humidity: %0.1f%%" % relative_humidity)
    else:
        temperature = 0
        relative_humidity = 0

    if ltr_status == 1:
        lux = ltr.lux
        if debug == 1:
            # Print UV Sensor Readings for Debugging Purposes
            print("UV:", ltr.uvs, "\t\tAmbient Light:", ltr.light)
            print("UVI:", ltr.uvi, "\t\tLux:", lux)
    else:
        lux = 0

    # Disable MUX channel
    test.disable_channels(chan)
    # Return Sensor Readings
    return temperature, relative_humidity, lux

# Disable all channels for fresh start
test.disable_all()

try:
    while True:
        # Read Sensors from first channel and account for precision error
        temperature, relative_humidity, lux = readSensors(0)
        temp_intervals = [[float(temperature) - 0.2, float(temperature) + 0.2]]
        hum_intervals = [[float(relative_humidity) - 2, float(relative_humidity) + 2]]
        #luxSet = [lux] # +- 10% of the output
        lux_intervals = [[float(lux) - float(lux/10), float(lux) + float(lux/10)]]

        # Read Sensors from second channel and account for precision error
        temperature, relative_humidity, lux = readSensors(3)
        temp_intervals.append([float(temperature) - 0.2, float(temperature) + 0.2])
        hum_intervals.append([float(relative_humidity) - 2, float(relative_humidity) + 2])
        #luxSet.append(lux)
        lux_intervals.append([float(lux) - float(lux/10), float(lux) + float(lux/10)])

        # Read Sensors from third channel and account for precision error
        temperature, relative_humidity, lux = readSensors(7)
        temp_intervals.append([float(temperature) - 0.2, float(temperature) + 0.2])
        hum_intervals.append([float(relative_humidity) - 2, float(relative_humidity) + 2])
        #luxSet.append(lux)
        lux_intervals.append([float(lux) - float(lux/10), float(lux) + float(lux/10)])



        if debug == 1:
            print("\nApplying Marzullo's Algorithm returns the following results: ")

        # Currently not using MA on Lux, instead just finding avg of 3 readings
        #avgLux = (luxSet[0] + luxSet[1] + luxSet[2])/3
        # Running Marzullo's Algorithm on Lux Readings
        N = len(lux_intervals)
        lowL, highL = marzulloAlgorithm(lux_intervals, N, 2)
        # Finding Median value
        medianL = (lowL+highL)/2
        # Finding new Precision variance
        luxMA = (highL - lowL)/2
        if debug == 1:
            print("Lux Precision is now: +/- %0.1f%%" % luxMA)
            print("Median Lux is: %0.1f" % medianL)
        # Adding current Lux to total lux over 24 Hours for Lux Hours Value
        # For Readings 1/min, 60 readings per hour, total 1440 readings per day
        if count%1440 == 0:
            luxHRs = 0
        #luxHRs = luxHRs + avgLux
        luxHRs = luxHRs + medianL
        if debug == 1:
            print("Current Lux is: ", medianL)
            print("Cumulative Lux Hours is: ", luxHRs)

        # Running Marzullo's Algorithm on Temperature Readings
        N = len(temp_intervals)
        lowT, highT = marzulloAlgorithm(temp_intervals, N, 0)
        # Finding Median value
        medianT = (lowT+highT)/2
        # Finding new Precision variance
        tempMA = (highT - lowT)/2
        if debug == 1:
            print("Temperature Precision is now: +/- %0.1f C" % tempMA)
            print("Median Temperature is: %0.1f C" % medianT)

        # Running Marzullo's Algorithm on Humidity Readings
        N = len(hum_intervals)
        lowH, highH = marzulloAlgorithm(hum_intervals, N, 1)
        # Finding Median value
        medianH = (lowH+highH)/2

        hum_over_hour[count%60] = medianH
        # Finding new Precision variance
        humMA = (highH - lowH)/2
        if debug == 1:
            print("Relative Humidity Precision is now: +/- %0.1f%%" % humMA)
            print("Median Relative Humidity is: %0.1f%%" % medianH)

            print("\n")

        # Testing Marzullo Output against Thresholds to determine if alert is triggered
        if (lowT < 20.5):
            if debug == 1:
                print("Below Soft Range of Acceptable Temp, LED02 On")
            if (lowT < 20):
                if debug == 1:
                    print("Below Hard Range of Acceptable Temp, LED04 On")
        if (highT > 21.5):
            if debug == 1:
                print("Above Soft Range of Acceptable Temp, LED01 On")
            if (highT > 22):
                if debug == 1:
                    print("Above Hard Range of Acceptable Temp, LED03 On")
        if (lowH < 40.0):
            if debug == 1:
                print("Below Soft Range of Acceptable Relative Humidity, LED06 On")
            if (lowH < 25.0):
                if debug == 1:
                    print("Below Hard Range of Acceptable Relative Humidity, LED08 On")
        if (highH > 50.0):
            if debug == 1:
                print("Above Soft Range of Acceptable Relative Humidity, LED05 On")
            if (highH > 65.0):
                if debug == 1:
                    print("Above Hard Range of Acceptable Relative Humidity, LED07 On")
        # If hum_over_hour list still has None values
        if count < 60:
            for x in range(count):
                if abs(hum_over_hour[x] - medianH) > 10:
                    if debug == 1:
                        print("Relative Humidity has changed more than 10% within an hour, LED09 On")
                        break
        else: # Code has run for more than an hour so safe to compare all items in list
            for x in hum_over_hour:
                if abs(x - medianH) > 10:
                    if debug == 1:
                        print("Relative Humidity has changed more than 10% within an hour, LED09 On")
                else:
                    if debug == 1:
                        print("Relative Humidity change is within threshold")
        if (lowL > 200) or (highL > 200):
            if debug == 1:
                print("Above Acceptable Level of Lux, LED10 On")
        if (luxHRs > 1000):
            if debug == 1:
                print("Above Acceptable Level of Lux Hours within 24 hours, LED11 On")

        if (ltr_down >= 3):
            if debug == 1:
                print("LTR Sensor Down 3 times, LED06 On")
        if (htu_down >= 3):
            if debug == 1:
                print("HTU Sensor Down 3 times, LED07 On")

        # Disabling Channels to ensure fresh start in next loop
        test.disable_all()

        # Getting Date/Time info for logging
        dateTimeObj = datetime.now()
        timeObj = dateTimeObj.time()
        dateObj = dateTimeObj.date()

        # Formatting data and writing it to log file.
        list = [dateObj.strftime("%b-%d-%Y"), timeObj.strftime("%H:%M:%S.%f"), medianT, medianH, medianL, luxHRs]
        logWrite(list)

        #Increase Loop Count at end of loop
        count = count + 1

        # Setting to 5 caused log entries every 6 seconds instead of 5
        time.sleep(4)
except KeyboardInterrupt:
    print("\n")
    pass
