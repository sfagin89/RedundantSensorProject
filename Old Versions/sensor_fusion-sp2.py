# Sensor Fusion using Marzullo's Algorithm
#
# Current Functionality:
# Takes in readings from each of the 3 sets of sensors using the MUX channels
# Outputs the results to the screen
# Using the known precision, creates pairs at the outer bounds of the precision
## for each reading to make a range of precision.
# Passes the Precious Range Pairs to a function that performs Marzullo's
## Algorithm and prints out the resulting 'improved' precision result.
# New Precision is now also printed (found by taking the difference between the
## upper and lower bound of the new range and dividing in half)
#
# Functionality to Add:
# Currently doesn't do anything for UV readings aside from output the sensor
## reading to the screen.
# If humidity has an absolute change of greater than 10% per hour, does the LED
## turn on to indicate fluctuation (Blinking Orange)
# Does system maintain 1 week of data for record keeping? - Wk 2, save output
## to CSV
## Sensor data (specify what exactly to save) should be saved for previous 7
## days (rolling/sliding) interab
# Alert should be produced if current light exposure is greater than 200 lux
# Alert should be produced if daily light exposure greater than 1000 lux hours
# Alert should be produced when a sensor, or multiple sensors fail
# Alert should be produced when a specific sensor remains down for
## (X time or Y cycles)
# Make sure Window Factor in UV sensor library is set correctly
## (for use in a windowless room)
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

#The name of this device
_DEFAULT_NAME = "Qwiic Mux"
_AVAILABLE_I2C_ADDRESS = [*range(0x70,0x77 + 1)]

# Instantiates an object for the MUX
test = qwiic.QwiicTCA9548A()

def marzulloAlgorithm(intervals,N,t):
    l = intervals[0][0]
    r = intervals[0][1]

    for i in range(1,N):
        if (intervals[i][0] > r or intervals[i][1] < l):
            continue
        else:
            l = max(l, intervals[i][0])
            r = min(r, intervals[i][1])

    if (t == 0):
        print("[%0.1f" % l,", %0.1f" % r,"]")
    elif (t == 1):
        print("[%0.1f%%" % l,", %0.1f%%" % r,"]")
    else:
        print("[",l,", ",r,"]")

    return l, r



#temp_readings[] #+/- 0.2 deg C accuracy
#hum_readings[] # +/- 2% accuracy
#uv_readings[]

# Disable all channels for fresh start
test.disable_all()

test.enable_channels(0)
i2c_0 = board.I2C()
ltr = adafruit_ltr390.LTR390(i2c_0)
htu = adafruit_htu31d.HTU31D(i2c_0)
print("\nSensor Series 1 has the following readings: ")
print("UV:", ltr.uvs, "\t\tAmbient Light:", ltr.light)
print("UVI:", ltr.uvi, "\t\tLux:", ltr.lux)
temperature, relative_humidity = htu.measurements
temp_readings = [float(temperature) - 0.2]
temp_readings.append(float(temperature) + 0.2)
temp_intervals=[[float(temperature) - 0.2, float(temperature) + 0.2]]
hum_readings = [float(relative_humidity) - 2]
hum_readings.append(float(relative_humidity) + 2)
hum_intervals=[[float(relative_humidity) - 2, float(relative_humidity) + 2]]
print("Temperature: %0.1f C" % temperature)
print("Humidity: %0.1f%%" % relative_humidity)
test.disable_channels(0)

test.enable_channels(3)
i2c_3 = board.I2C()
ltr = adafruit_ltr390.LTR390(i2c_3)
htu = adafruit_htu31d.HTU31D(i2c_3)
print("\nSensor Series 2 has the following readings: ")
print("UV:", ltr.uvs, "\t\tAmbient Light:", ltr.light)
print("UVI:", ltr.uvi, "\t\tLux:", ltr.lux)
temperature, relative_humidity = htu.measurements
temp_readings.append(float(temperature) - 0.2)
temp_readings.append(float(temperature) + 0.2)
temp_intervals.append([float(temperature) - 0.2, float(temperature) + 0.2])
hum_readings.append(float(relative_humidity) - 2)
hum_readings.append(float(relative_humidity) + 2)
hum_intervals.append([float(relative_humidity) - 2, float(relative_humidity) + 2])
print("Temperature: %0.1f C" % temperature)
print("Humidity: %0.1f%%" % relative_humidity)
test.disable_channels(3)

test.enable_channels(7)
i2c_7 = board.I2C()
ltr = adafruit_ltr390.LTR390(i2c_7)
htu = adafruit_htu31d.HTU31D(i2c_7)
print("\nSensor Series 3 has the following readings: ")
print("UV:", ltr.uvs, "\t\tAmbient Light:", ltr.light)
print("UVI:", ltr.uvi, "\t\tLux:", ltr.lux)
temperature, relative_humidity = htu.measurements
temp_readings.append(float(temperature) - 0.2)
temp_readings.append(float(temperature) + 0.2)
temp_intervals.append([float(temperature) - 0.2, float(temperature) + 0.2])
hum_readings.append(float(relative_humidity) - 2)
hum_readings.append(float(relative_humidity) + 2)
hum_intervals.append([float(relative_humidity) - 2, float(relative_humidity) + 2])
print("Temperature: %0.1f C" % temperature)
print("Humidity: %0.1f%%" % relative_humidity)
test.disable_channels(7)

print("\nApplying Marzullo's Algorithm returns the following results: ")
#Returns the smallest interval consistent with largest number of sources

#for n in temp_readings:
#    print("%0.1f" % n)

#for n in hum_readings:
#    print("%0.1f%%" % n)

#print('\n'.join([''.join(['{:4}'.format(item) for item in row])
#      for row in temp_intervals]))

N = len(temp_intervals)
lowT, highT = marzulloAlgorithm(temp_intervals, N, 0)
#print(type(low))
#print(type(high))
tempMA = (highT - lowT)/2
print("Temperature Precision is now: +/- %0.1f C" % tempMA)

N = len(hum_intervals)
lowH, highH = marzulloAlgorithm(hum_intervals, N, 1)
#print(type(low))
#print(type(high))
humMA = (highH - lowH)/2
print("Relative Humidity Precision is now: +/- %0.1f%%" % humMA)

print("\n")

if (lowT < 20.5):
    print("Below Soft Range of Acceptable Temp, LED01 On")
    if (lowT < 20):
        print("Below Hard Range of Acceptable Temp, LED02 On")
if (highT > 21.5):
    print("Above Soft Range of Acceptable Temp, LED01 On")
    if (highT > 22):
        print("Above Hard Range of Acceptable Temp, LED02 On")
if (lowH < 40.0):
    print("Below Soft Range of Acceptable Relative Humidity, LED01 On")
    if (lowH < 25.0):
        print("Below Hard Range of Acceptable Relative Humidity, LED02 On")
if (highH > 50.0):
    print("Above Soft Range of Acceptable Relative Humidity, LED01 On")
    if (highH > 65.0):
        print("Above Hard Range of Acceptable Relative Humidity, LED02 On")

test.disable_all()

#while True:
#    print("UV:", ltr.uvs, "\t\tAmbient Light:", ltr.light)
#    print("UVI:", ltr.uvi, "\t\tLux:", ltr.lux)
#    time.sleep(1.0)
#    temperature, relative_humidity = htu.measurements
#    print("Temperature: %0.1f C" % temperature)
#    print("Humidity: %0.1f %%" % relative_humidity)
#    print("")
#    time.sleep(1)
