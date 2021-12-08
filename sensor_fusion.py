# Sensor Fusion using Marzullo's Algorithm
#
# Current Functionality:
# Takes in readings from each of the 3 sets of sensors using the MUX channels
# Outputs the results to the screen when debug mode is enabled.
# Using the known precision, creates pairs at the outer bounds of the precision
## for each reading to make a range of precision.
# Passes the Precision Range Pairs to a function that performs Marzullo's
## Algorithm and returns the resulting new range.
# New Precision is now also printed (found by taking the difference between the
## upper and lower bound of the new range and dividing in half)
# Median value of the new range is also found
# Lower and Upper bounds of new range is used to test against LED triggers
# Writes Date, Time, Temp, and Humidity Readings, Sensor Status, and LED states
## to CSV file. Currently appends each new set of values to the next line of the
## CSV file.
# A new log file is created each day.
# If humidity has an absolute change of greater than 10% per hour, Alert is
## triggered.
# Alert is produced if current light exposure is greater than 200 lux
# Alert is produced if daily light exposure greater than 1000 lux hours
# Debug Mode implemented: If debug set to 1, print states will execute to aid in
## debugging.
# Alert is produced when any sensor in a series fails.
# Alert is produced when a specific sensor series remains down for 3 cycles
# Overall Loop is intended to run once per minute. For demonstration purposes,
## the sleep time at the end of the loop can be changed to run more frquently
#
# Customizing Functionality:
## Sensor Thresholds have been set as variable values to allow easy adjustment
## to suit any implementation.

import time
import qwiic
import board
import adafruit_htu31d
import adafruit_ltr390
import csv
import os
import RPi.GPIO as GPIO
from datetime import datetime


#The name of this device
_DEFAULT_NAME = "Qwiic Mux"
_AVAILABLE_I2C_ADDRESS = [*range(0x70,0x77 + 1)]

# Sets Debug Mode (1 = On)
## Set to 0 to disable Print Statements
debug = 1

# LED GPIO
## Temp Greather/Less than Soft/Hard Thresholds
led_temp_gthard = 26
led_temp_gtsoft = 21
led_temp_ltsoft = 19
led_temp_lthard = 20
## Hum Greather/Less than Soft/Hard Thresholds
led_hum_gthard = 16
led_hum_gtsoft = 13
led_hum_ltsoft = 6
led_hum_lthard = 12
## Humidity Change >10% /hr
led_hum_chng = 5
## Current Lux threshold Exceeded
led_lux_gt = 7
## LuxHours threshold over 24hrs Exceeded
led_luxhr_gt = 8
## Either/Both Sensors in Series Currently Down
led_s01_err = 25
led_s02_err = 11
led_s03_err = 9
## Either/Both Sensors in Series Down for 3 or more Cycles
led_s01_dwn = 10
led_s02_dwn = 24
led_s03_dwn = 23

# Value to hold Cumulative Lux Hours over 24hr Period
luxHRs = 0

# Loop Counter
count = 0

# Indicates current status of each sensor series (1-3)
# Set to 1 each time sensor is down, triggers LED at 1
sensor_error = [0, 0, 0]
# Indicates historic status of each sensor series (1-3)
# Increments when sensor_error is 1, triggers LED at 3
sensor_down = [0, 0, 0]

# List for Humidity Values over hour period to check for >10% change
## 1 reading per minute = 60 readings per hour
hum_over_hour = [None] * 60

# Sensor Thresholds based on Specifications
## Temperature Thresholds (degrees Celsius)
#temp_lh = 20    # low/hard threshold
#temp_ls = 20.5  # low/soft threshold
#temp_hs = 21.5  # high/soft threshold
#temp_hh = 22    # high/hard threshold
## Relative Humidity Thresholds (Percentage)
#hum_lh = 35.0   # low/hard threshold
#hum_ls = 40.0   # low/soft threshold
#hum_hs = 50.0   # high/soft threshold
#hum_hh = 55.0   # high/hard threshold
#hum_hrch = 10   # low/hard threshold
## Lux & LuxHrs Thresholds
#lux_max = 200
#luxhr_max = 1000

# Sensor Thresholds based on Demo Requirement
temp_baseline = 0#current room value
hum_baseline = 0#current room value
lux_baseline = 0#current room value
## Temperature Thresholds (degrees Celsius)
temp_lh = temp_baseline + 4    # low/hard threshold
temp_ls = temp_baseline + 8  # low/soft threshold
temp_hs = temp_baseline + 12  # high/soft threshold
temp_hh = temp_baseline + 16    # high/hard threshold
## Relative Humidity Thresholds (Percentage)
hum_lh = 10   # low/hard threshold
hum_ls = -5   # low/soft threshold
hum_hs = +10   # high/soft threshold
hum_hh = +15   # high/hard threshold
hum_hrch = 10   # low/hard threshold
## Lux & LuxHrs Thresholds
lux_max = lux_baseline * 5
luxhr_max = lux_baseline * 10

# Instantiates an object for the MUX
mux = qwiic.QwiicTCA9548A()


# Runs Marzullo's Algorithm on a set of data pairs
# Returns the smallest interval consistent with largest number of sources
## intervals = The set of data pairs passed to the function
## N = The number of pairs sent (The length)
## t = The type of data, used for formatting the output
def marzulloAlgorithm(intervals,N,t):

    intervals.sort()
    m_left = intervals[0][0]
    m_right = intervals[0][1]

    #if debug == 1:
    #    print("Sorted Values received by Marzullo")
    #    for x in range(0,N):
    #        print("[",intervals[x][0],", ",intervals[x][1],"]")

    m_intersections = 0 #Interval with highest number of intersections
    for j in range(0,N):
        l = intervals[j][0]
        r = intervals[j][1]
        c_intersections = 0 #Current number of intersections

        # Checking for Intersections of current interval with other intervals
        for i in range(0,N):
            if (intervals[i][0] > r or intervals[i][1] < l):
                # No intersection
                continue
            else:
                l = max(l, intervals[i][0])
                r = min(r, intervals[i][1])
                c_intersections = c_intersections + 1

        if c_intersections > m_intersections:
            m_intersections = c_intersections
            m_left = l
            m_right = r

    if debug == 1:
        if (t == 0):
            print("\nNew Temperature Range: [%0.1f C" % m_left,", %0.1f C" % m_right,"]")
        elif (t == 1):
            print("\nNew Humidity Range: [%0.1f%%" % m_left,", %0.1f%%" % m_right,"]")
        else:
            print("\nNew Lux Range: [%0.1f" % m_left,", %0.1f" % m_right,"]")

    return m_left, m_right

# Writes data to a CSV log file. If file doesn't exist a new one is created
## dataList = data to append to next line of CSV log file
def logWrite(dataList):
    dateTimeObj = datetime.now()
    dateObj = dateTimeObj.date()
    currentDate = dateObj.strftime("%b-%d-%Y")
    file = "sensor_log_"+currentDate+".csv"
    headers = ['Date', 'Time Stamp', 'Temperature', 'Relative Humidity',
    'Current Lux', 'Cumulative Lux Hours', 'Series 1', 'Series 2', 'Series 3',
    'L01', 'L02', 'L03', 'L04', 'L05', 'L06', 'L07', 'L08', 'L09', 'L10', 'L11',
    'L12', 'L13', 'L14', 'L15', 'L16', 'L17']

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
    mux.enable_channels(chan)
    # Read the data from the LTR390 and HTU31D sensors
    i2c = board.I2C()
    ## 1 = sensor is up, 0 = sensor is down
    ltr_status = 0
    htu_status = 0
    up_down = 0

    #Checking if UV sensor is reachable at i2c address
    try:
        if debug == 1:
            print("\nChecking LTR Sensor")
        ltr = adafruit_ltr390.LTR390(i2c)
        ltr_status = 1
    except ValueError as error1:
        print("\t", error1)
        if debug == 1:
            print("\tLTR Sensor Down")

    #Checking if temp/hum sensor is reachable at i2c address
    try:
        if debug == 1:
            print("Checking HTU Sensor")
        htu = adafruit_htu31d.HTU31D(i2c)
        htu_status = 1
    except ValueError as error2:
        print("\t", error2)
        if debug == 1:
            print("\tHTU Sensor Down")

    #If either sensor is down, treat whole series as down
    if (ltr_status == 0) or (htu_status == 0):
        up_down = 1
        temperature = 0
        relative_humidity = 0
        lux = 0
        if debug == 1:
            print("\nSensor Series Down")
    else:
        if debug == 1:
            print("\nSensor Series has the following readings: ")

        if htu_status == 1: #Double checking sensor is up
            temperature, relative_humidity = htu.measurements
            temperature = round(temperature, 2)
            relative_humidity = round(relative_humidity, 2)
            if debug == 1:
                # Print Temp & Humidity Sensor Readings for Debugging Purposes
                print("\tTemperature: %0.1f C" % temperature)
                print("\tHumidity: %0.1f%%" % relative_humidity)
        else:
            temperature = 0
            relative_humidity = 0

        if ltr_status == 1: #Double checking sensor is up
            lux = ltr.lux
            lux = round(lux, 2)
            if debug == 1:
                # Print UV Sensor Readings for Debugging Purposes
                #EDIT 03: Formatted output of non-saved values for readability
                print("\tUV: %0.1f" % ltr.uvs, "\t\tAmbient Light: %0.1f" % ltr.light)
                print("\tUVI: %0.1f" % ltr.uvi, "\t\tLux: %0.1f" % lux)
        else:
            lux = 0

    # Disable MUX channel
    mux.disable_channels(chan)

    # Return Sensor Readings
    return temperature, relative_humidity, lux, up_down

def led_setup():
    led_list = [led_temp_gtsoft, led_temp_ltsoft, led_temp_gthard, led_temp_lthard,
    led_hum_gtsoft, led_hum_ltsoft, led_hum_gthard, led_hum_lthard, led_hum_chng,
    led_lux_gt, led_luxhr_gt, led_s01_err, led_s02_err, led_s03_err, led_s01_dwn,
    led_s02_dwn, led_s03_dwn]

    GPIO.setmode(GPIO.BCM)
    for x in led_list:
        GPIO.setup(x, GPIO.OUT)
        GPIO.output(x, GPIO.LOW)

def led_cleanup():
    led_list = [led_temp_gtsoft, led_temp_ltsoft, led_temp_gthard, led_temp_lthard,
    led_hum_gtsoft, led_hum_ltsoft, led_hum_gthard, led_hum_lthard, led_hum_chng,
    led_lux_gt, led_luxhr_gt, led_s01_err, led_s02_err, led_s03_err, led_s01_dwn,
    led_s02_dwn, led_s03_dwn]

    for x in led_list:
        GPIO.output(x, GPIO.LOW)
    GPIO.cleanup()


# Disable all channels for fresh start
mux.disable_all()
led_setup()

try:
    while True:

        ########################################################################
        # Sensor Reading Stage:                                                #
        # Each Sensor Series is read by opoening the relevant mux channel,     #
        # reading in the data, then closing the channel and returning the data #
        # to the main script.                                                  #
        # Each set of readings is then adjusted into an upper and lower bound  #
        # based on the known precision of the sensors. Then added as a pair to #
        # a list of tuples. One list each for temp, humidity and lux           #
        # The up/down status of the sensors is also returned. If one sensor in #
        # a series is down, the entire series is treated as down for the rest  #
        # of the loop.                                                         #
        # More sensor series can be used by adding additional blocks           #
        # (3 Currently in use), Current Mux suports 8                          #
        ########################################################################

        temp_intervals = []
        hum_intervals = []
        lux_intervals = []

        # Read Sensors from first channel and account for precision error
        temperature, relative_humidity, lux, sensor_error[0] = readSensors(0)
        if (sensor_error[0] == 0):
            sensor_down[0] = 0
            temp_intervals.append([float(temperature) - 0.2, float(temperature) + 0.2])
            hum_intervals.append([float(relative_humidity) - 2, float(relative_humidity) + 2])
            lux_intervals.append([float(lux) - float(lux/10), float(lux) + float(lux/10)])
        else:
            sensor_down[0] = sensor_down[0] + sensor_error[0]

        # Read Sensors from second channel and account for precision error
        temperature, relative_humidity, lux, sensor_error[1] = readSensors(3)
        if (sensor_error[1] == 0):
            sensor_down[1] = 0
            temp_intervals.append([float(temperature) - 0.2, float(temperature) + 0.2])
            hum_intervals.append([float(relative_humidity) - 2, float(relative_humidity) + 2])
            lux_intervals.append([float(lux) - float(lux/10), float(lux) + float(lux/10)])
        else:
            sensor_down[1] = sensor_down[1] + sensor_error[1]

        # Read Sensors from third channel and account for precision error
        temperature, relative_humidity, lux, sensor_error[2] = readSensors(7)
        if (sensor_error[2] == 0):
            sensor_down[2] = 0
            temp_intervals.append([float(temperature) - 0.2, float(temperature) + 0.2])
            hum_intervals.append([float(relative_humidity) - 2, float(relative_humidity) + 2])
            lux_intervals.append([float(lux) - float(lux/10), float(lux) + float(lux/10)])
        else:
            sensor_down[2] = sensor_down[2] + sensor_error[2]

        ########################################################################
        # Marzullo's Algorithm Stage:                                          #
        # If at least 2 sensors are up, sensor readings are sent to the        #
        # MarzulloAlgorithm function as a series of intervals. If only 1       #
        # sensor is up, that sensor's reading is set as the low/high values.   #
        # If no sensors are up, low/high values are set to 0. From the         #
        # low/high values, the new precision and median values are found. The  #
        # low/high values are used to check against LED triggers, except for   #
        # Cummulative LuxHrs, which uses the median lux value, and the change  #
        # in Humidity over an hour period.                                     #
        ########################################################################

        if debug == 1:
            print("\nApplying Marzullo's Algorithm returns the following results:")

        # Running Marzullo's Algorithm on Lux Readings
        N = len(lux_intervals)

        if (sensor_error[0]+sensor_error[1]+sensor_error[2] < 2):
            lowL, highL = marzulloAlgorithm(lux_intervals, N, 2)
        elif (sensor_error[0]+sensor_error[1]+sensor_error[2] == 2):
            lowL, highL = 0, 0
            for x in range(0,N):
                lowL = lowL + lux_intervals[x][0]
                highL = highL + lux_intervals[x][1]
        else:
            lowL, highL = 0, 0

        # Finding Median value
        medianL = (lowL+highL)/2
        medianL = round(medianL, 2)
        # Finding new Precision variance
        if medianL == 0:
            luxMA = 0
        else:
            luxMA = ((highL - lowL)/2)/medianL * 100
        luxMA = round(luxMA, 2)
        if debug == 1:
            print("\tLux Precision is now: +/- %0.1f%%" % luxMA)
            print("\tMedian Lux is: %0.1f" % medianL)
        # Adding current Lux to total lux over 24 Hours for Lux Hours Value
        # For Readings 1/min, 60 readings per hour, total 1440 readings per day
        if count%1440 == 0:
            luxHRs = 0
        #luxHRs = luxHRs + avgLux
        luxHRs = luxHRs + medianL
        luxHRs = round(luxHRs, 2)
        if debug == 1:
            print("\tCumulative Lux Hours is: ", luxHRs)

        # Running Marzullo's Algorithm on Temperature Readings
        N = len(temp_intervals)
        if (sensor_error[0]+sensor_error[1]+sensor_error[2] < 2):
            lowT, highT = marzulloAlgorithm(temp_intervals, N, 0)
        elif (sensor_error[0]+sensor_error[1]+sensor_error[2] == 2):
            lowT, highT = 0, 0
            for x in range(0,N):
                lowT = lowT + temp_intervals[x][0]
                highT = highT + temp_intervals[x][1]
        else:
            lowT, highT = 0, 0

        # Finding Median value
        medianT = (lowT+highT)/2
        medianT = round(medianT, 2)
        # Finding new Precision variance
        tempMA = (highT - lowT)/2
        tempMA = round(tempMA, 2)
        if debug == 1:
            print("\tTemperature Precision is now: +/- %0.1f C" % tempMA)
            print("\tMedian Temperature is: %0.1f C" % medianT)

        # Running Marzullo's Algorithm on Humidity Readings
        N = len(hum_intervals)
        if (sensor_error[0]+sensor_error[1]+sensor_error[2] < 2):
            lowH, highH = marzulloAlgorithm(hum_intervals, N, 1)
        elif (sensor_error[0]+sensor_error[1]+sensor_error[2] == 2):
            lowH, highH = 0, 0
            for x in range(0,N):
                lowH = lowH + hum_intervals[x][0]
                highH = highH + hum_intervals[x][1]
        else:
            lowH, highH = 0, 0

        # Finding Median value
        medianH = (lowH+highH)/2
        medianH = round(medianH, 2)

        hum_over_hour[count%60] = medianH
        # Finding new Precision variance
        humMA = (highH - lowH)/2
        humMA = round(humMA, 2)
        if debug == 1:
            print("\tRelative Humidity Precision is now: +/- %0.1f%%" % humMA)
            print("\tMedian Relative Humidity is: %0.1f%%\n" % medianH)

        ########################################################################
        # LED/Actuator Driver Stage:                                           #
        # Values found using Marzullo's Algorithm are compared against the set #
        # thresholds. If they exceed the threshold, the relevant LED is set to #
        # high. Else it is set back to low.                                    #
        # LED status is also recorded to be written to the Log file.           #
        ########################################################################

        # Testing Marzullo Output against Thresholds to determine if alert is triggered
        #EDIT #: Added list to hold LED status for Log file
        led_log = ["0"] * 17
        #EDIT 04: Fixed Swapped LED Print Statements

        # Is temperature below soft or hard thresholds.
        ## LED HIGH if yes. LED LOW if no
        if (lowT < temp_ls):
            GPIO.output(led_temp_ltsoft, GPIO.HIGH)
            led_log[2] = "1"
            if debug == 1:
                print("Below Soft Range of Acceptable Temp, LED03 On")
            if (lowT < temp_lh):
                GPIO.output(led_temp_lthard, GPIO.HIGH)
                led_log[3] = "1"
                if debug == 1:
                    print("Below Hard Range of Acceptable Temp, LED04 On")
            else:
                GPIO.output(led_temp_lthard, GPIO.LOW)
                led_log[3] = "0"
        else:
            GPIO.output(led_temp_ltsoft, GPIO.LOW)
            led_log[2] = "1"

        # Is temperature above soft or hard thresholds.
        ## LED HIGH if yes. LED LOW if no
        if (highT > temp_hs):
            GPIO.output(led_temp_gtsoft, GPIO.HIGH)
            led_log[1] = "1"
            if debug == 1:
                print("Above Soft Range of Acceptable Temp, LED02 On")
            if (highT > temp_hh):
                GPIO.output(led_temp_gthard, GPIO.HIGH)
                led_log[0] = "1"
                if debug == 1:
                    print("Above Hard Range of Acceptable Temp, LED01 On")
            else:
                GPIO.output(led_temp_gthard, GPIO.LOW)
                led_log[0] = "0"
        else:
            GPIO.output(led_temp_gtsoft, GPIO.LOW)
            led_log[1] = "0"

        # Is relative humidity below soft or hard thresholds.
        ## LED HIGH if yes. LED LOW if no
        if (lowH < hum_ls):
            GPIO.output(led_hum_ltsoft, GPIO.HIGH)
            led_log[6] = "1"
            if debug == 1:
                print("Below Soft Range of Acceptable Relative Humidity, LED07 On")
            if (lowH < hum_lh):
                GPIO.output(led_hum_lthard, GPIO.HIGH)
                led_log[7] = "1"
                if debug == 1:
                    print("Below Hard Range of Acceptable Relative Humidity, LED08 On")
            else:
                GPIO.output(led_hum_lthard, GPIO.LOW)
                led_log[7] = "0"
        else:
            GPIO.output(led_hum_ltsoft, GPIO.LOW)
            led_log[6] = "0"

        # Is relative humidity above soft or hard thresholds.
        ## LED HIGH if yes. LED LOW if no
        if (highH > hum_hs):
            GPIO.output(led_hum_gtsoft, GPIO.HIGH)
            led_log[5] = "1"
            if debug == 1:
                print("Above Soft Range of Acceptable Relative Humidity, LED06 On")
            if (highH > hum_hh):
                GPIO.output(led_hum_gthard, GPIO.HIGH)
                led_log[4] = "1"
                if debug == 1:
                    print("Above Hard Range of Acceptable Relative Humidity, LED05 On")
            else:
                GPIO.output(led_hum_gthard, GPIO.LOW)
                led_log[4] = "0"
        else:
            GPIO.output(led_hum_gtsoft, GPIO.LOW)
            led_log[5] = "0"

        # Has relative humidity changed more than 10% in 1 hr
        ## LED HIGH if yes. LED LOW if no
        if count < 60: # If hum_over_hour list still has 'None' values
            for x in range(count):
                if abs(hum_over_hour[x] - medianH) > hum_hrch:
                    GPIO.output(led_hum_chng, GPIO.HIGH)
                    led_log[8] = "1"
                    if debug == 1:
                        print("Relative Humidity has changed more than 10% within an hour, LED09 On")
                        break
        else: # Code has run for more than an hour so safe to compare all items in list
            for x in hum_over_hour:
                if abs(x - medianH) > hum_hrch:
                    GPIO.output(led_hum_chng, GPIO.HIGH)
                    led_log[8] = "1"
                    if debug == 1:
                        print("Relative Humidity has changed more than 10% within an hour, LED09 On")
                #else:
                #    if debug == 1:
                #        print("Relative Humidity change is within threshold")

        # Has Lux exceeded threshold in single reading
        ## LED HIGH if yes. LED LOW if no
        if (lowL > lux_max) or (highL > lux_max):
            GPIO.output(led_lux_gt, GPIO.HIGH)
            led_log[9] = "1"
            if debug == 1:
                print("Above Acceptable Level of Lux, LED10 On")
        else:
            GPIO.output(led_lux_gt, GPIO.LOW)
            led_log[9] = "0"

        # Has Luxhr exceeded threshold in 24hr period
        ## LED HIGH if yes. LED LOW if no
        if (luxHRs > luxhr_max):
            GPIO.output(led_luxhr_gt, GPIO.HIGH)
            led_log[10] = "1"
            if debug == 1:
                print("Above Acceptable Level of Lux Hours within 24 hours, LED11 On")
        else:
            GPIO.output(led_luxhr_gt, GPIO.LOW)
            led_log[10] = "0"

        # Are Sensors Down for current cycle
        ## LED HIGH if yes. LED LOW if no

        ## Checking Sensor Series 1 Status
        if sensor_error[0] == 1:
            GPIO.output(led_s01_err, GPIO.HIGH)
            led_log[11] = "1"
            if debug == 1:
                print("Sensor Series 1 down, LED12 On")
        else:
            GPIO.output(led_s01_err, GPIO.LOW)
            led_log[11] = "0"

        ## Checking Sensor Series 2 Status
        if sensor_error[1] == 1:
            GPIO.output(led_s02_err, GPIO.HIGH)
            led_log[12] = "0"
            if debug == 1:
                print("Sensor Series 2 down, LED13 On")
        else:
            GPIO.output(led_s02_err, GPIO.LOW)
            led_log[12] = "0"

        ## Checking Sensor Series 3 Status
        if sensor_error[2] == 1:
            GPIO.output(led_s03_err, GPIO.HIGH)
            led_log[13] = "1"
            if debug == 1:
                print("Sensor Series 3 down, LED14 On")
        else:
            GPIO.output(led_s03_err, GPIO.LOW)
            led_log[13] = "0"

        ## Have sensors been down for 3 consecutive cycles?
        ## LED HIGH if yes. Does not reset once triggered.

        ## Checking Sensor Series 1
        if sensor_down[0] >= 3:
            GPIO.output(led_s01_dwn, GPIO.HIGH)
            led_log[14] = "1"
            if debug == 1:
                print("Sensor Series 1 down 3 times in a row, LED15 On")

        ## Checking Sensor Series 2
        if sensor_down[1] >= 3:
            GPIO.output(led_s02_dwn, GPIO.HIGH)
            led_log[15] = "1"
            if debug == 1:
                print("Sensor Series 2 down 3 times in a row, LED16 On")

        ## Checking Sensor Series 3
        if sensor_down[2] >= 3:
            GPIO.output(led_s03_dwn, GPIO.HIGH)
            led_log[16] = "1"
            if debug == 1:
                print("Sensor Series 3 down 3 times in a row, LED17 On")

        # Disabling Channels to ensure fresh start in next loop
        mux.disable_all()

        # Getting Date/Time info for logging
        dateTimeObj = datetime.now()
        timeObj = dateTimeObj.time()
        dateObj = dateTimeObj.date()

        # Setting Values for Sensor Status In Log file
        sensor_log = [None] * len(sensor_error)
        stat_count = 0
        for x in sensor_error:
            if x == 0:
                sensor_log[stat_count] = "Up"
            else:
                sensor_log[stat_count] = "Down"
            stat_count = stat_count + 1

        # Formatting data and writing it to log file.
        list = [dateObj.strftime("%b-%d-%Y"), timeObj.strftime("%H:%M:%S.%f"),
        medianT, medianH, medianL, luxHRs, sensor_log[0], sensor_log[1],
        sensor_log[2], led_log[0], led_log[1], led_log[2], led_log[3],
        led_log[4], led_log[5], led_log[6], led_log[7], led_log[8], led_log[9],
        led_log[10], led_log[11], led_log[12], led_log[13], led_log[14],
        led_log[15], led_log[16]]
        logWrite(list)

        #Increase Loop Count at end of loop
        count = count + 1

        # Setting to 5 caused log entries every 6 seconds instead of 5
        time.sleep(4)
except KeyboardInterrupt:
    #GPIO.cleanup()
    led_cleanup()
    print("\n")
    pass
