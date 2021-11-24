# SPDX-FileCopyrightText: 2021 by Bryan Siepert, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
#
# Added error handling for if sensor is Unreachable
import time
import board
import adafruit_ltr390

i2c = board.I2C()
try:
    print("Trying to access Sensor")
    ltr = adafruit_ltr390.LTR390(i2c)
    sensor_status = 1
    print("Sensor Reached")
except ValueError as error:
    print(error)
    print("Value Error thrown. Sensor Appears to be Unreachable.")
    sensor_status = 0

while True:
    if sensor_status == 1:
        print("UV:", ltr.uvs, "\t\tAmbient Light:", ltr.light)
        print("UVI:", ltr.uvi, "\t\tLux:", ltr.lux)

    if sensor_status == 0:
        print("Sensor Unreachable")

    time.sleep(1.0)
