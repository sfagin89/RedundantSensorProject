# Redundant Sensor Project
Repo for the Redundant Archival Preservation System using Sensor Fusion

<p align="center">
  <img src="https://github.com/sfagin89/RedundantSensorProject/blob/main/Images/Final_Layout.jpg">
</p>

A demonstration of this project can be viewed on YouTube.

[![Redundant Archival Preservation System Demo](https://img.youtube.com/vi/ZMbAT5cT7FY/1.jpg)](https://www.youtube.com/watch?v=ZMbAT5cT7FY)

## Project Overview

This project is intended to be used as a redundant sensor application, applying Marzullo's Algorithm to improve the precision error of sensor readings. The focus is on monitoring environmental conditions in relation to preserving archival material, however it can be used in many other scenarios, as the sensor thresholds are easily changed depending on your requirements, as well as swapping out the Temperature/Humidity and UV/Light sensors used in this project for other sensors.

The images below display the results of Marzullo's Algorithm when applied to a set of 3 UV Light sensor readings. The LTR390 Sensor has a known precision error of +/- 10%[^3]. After running through the script's MarzulloAlgorithm function, the new precision error of the result is +/- 7.7%.

<p align="center">
  <img src="https://github.com/sfagin89/RedundantSensorProject/blob/main/Images/Marzullo_Applied_to_Light_Sensor.png">
</p>

<p align="center">
  <img src="https://github.com/sfagin89/RedundantSensorProject/blob/main/Images/Marzullo_Applied_Line_Graph.png">
</p>

## Thresholds

The threshold values used to compare against the sensor readings and trigger LED alerts are set at the top of the script as a series of global variables. To change which level of sensor readings the application should react to, these threshold values are what need to be adjusted. Listed below are the current threshold settings, designed after researching the recommended environmental conditions for storing paper and ink based items[^4][^5].

* Temperature & Humidity
  * Hard Temperature Thresholds of 20-22 Degrees Celsius
    * Soft Temperature Thresholds of 20.5-21.5 Degrees Celsius was implemented as well.
  * Hard Humidity Thresholds of 35-55% Relative Humidity
    * Soft Humidity Thresholds of 40-50% Relative Humidity was implemented as well.
  * Humidity should not change more than 10% per hour.
* Light Levels
  * Light exposure should not exceed 200 Lux in a single instance.
  * Light exposure over an period of 24 hours should not exceed 1000 Lux Hours.

Note: The soft thresholds are meant to act as an early warning system as the sensor readings approach the outer range of the recommended conditions.

## Software

The python script **sensor_fusion.py** runs all aspects of this project. Instructions to run it can be found [HERE](https://github.com/sfagin89/RedundantSensorProject#running-the-application). Non built-in python libraries that must be installed are included in the RPi Setup instructions [HERE](https://github.com/sfagin89/RedundantSensorProject#first-boot-setup)

<p align="center">
  <img src="https://github.com/sfagin89/RedundantSensorProject/blob/main/Images/EC545%20High%20Level%20Software%20Diagram.png">
</p>

Additional details on how the script works and what can be altered are included in the script comments.

## Hardware Setup
### Parts List
* 1x Raspberry Pi 4 Model B
  * https://www.raspberrypi.com/products/raspberry-pi-4-model-b/
* 1x SparkFun Qwiic SHIM for Raspberry Pi
  * https://www.sparkfun.com/products/15794
  * https://learn.sparkfun.com/tutorials/qwiic-shim-for-raspberry-pi-hookup-guide
* 1x SparkFun Qwiic Mux Breakout - 8 Channel (TCA9548A)
  * https://www.sparkfun.com/products/16784
  * https://learn.sparkfun.com/tutorials/qwiic-mux-hookup-guide
  * 10x Qwiic Connectors
    * 2x Pass Through (Daisy Chain)
    * 8x Channels
  * I2C Address: 0x70 (default) up to 0x77
  * https://cdn.sparkfun.com/assets/f/0/4/b/3/tca9548a.pdf
* 3x Adafruit HTU31 Temperature & Humidity Sensor Breakout Board - STEMMA QT / Qwiic
  * https://www.adafruit.com/product/4832
  * 2x Qwiic Connectors
  * I2C Address: 0x40 or 0x41
* 3x Adafruit LTR390 UV Light Sensor - STEMMA QT / Qwiic
  * https://www.adafruit.com/product/4831
  * https://learn.adafruit.com/adafruit-ltr390-uv-sensor
  * https://learn.adafruit.com/adafruit-ltr390-uv-sensor/python-circuitpython
  * 2x Qwiic Connectors
  * I2C Address: 0x53

### Assembly
The remainder of this guide and the provided code assumes the Pi, Sensors, and LEDs have been assembled following these instructions:

#### Raspberry Pi 4 GPIO Pinout, refer to [this diagram](https://github.com/sfagin89/RedundantSensorProject/blob/main/Images/RPi4_GPIO_pinout_diagram.png) for a visual pinout.
  * (PIN 37) GPIO 26 -> LED01 (Red)
  * (PIN 40) GPIO 21 -> LED02 (Orange)
  * (PIN 35) GPIO 19 -> LED03 (Green)
  * (PIN 38) GPIO 20 -> LED04 (Blue)
  * (PIN 36) GPIO 16 -> LED05 (Red)
  * (PIN 33) GPIO 13 -> LED06 (Orange)
  * (PIN 31) GPIO 06 -> LED07 (Green)
  * (PIN 32) GPIO 12 -> LED08 (Blue)
  * (PIN 29) GPIO 05 -> LED09 (Orange)
  * (PIN 26) GPIO 07 -> LED10 (Red)
  * (PIN 24) GPIO 08 -> LED11 (Red)
  * (PIN 22) GPIO 25 -> LED12 (Orange)
  * (PIN 23) GPIO 11 -> LED13 (Orange)
  * (PIN 21) GPIO 09 -> LED14 (Orange)
  * (PIN 19) GPIO 10 -> LED15 (Red)
  * (PIN 18) GPIO 24 -> LED16 (Red)
  * (PIN 16) GPIO 23 -> LED17 (Red)
  * (PIN 39) -> Ground

If the 'friction' connection for the Qwiic SHIM isn't maintaining a consistent connection, I'd recommend soldering a set of jumpers to the SHIM and connect it to the GPIO via jumper wires, using the following Pinouts
  * (PIN 01) -> 3.3v
  * (PIN 02) -> 5v
  * (PIN 03) -> I2C SD
  * (PIN 04) -> 5v
  * (PIN 05) -> I2C SC
  * (PIN 06) -> Ground

#### Breadboard LED Layout
![LED Layout for Breadboard](https://github.com/sfagin89/RedundantSensorProject/blob/main/Images/Breadboard_LED_Layout.png?raw=true)

### Overall Layout

When assembled, the project should match the design shown below:
<p align="center">
  <img src="https://github.com/sfagin89/RedundantSensorProject/blob/main/Images/EC545_schematic_bb.png" height="625">
</p>

## Setting Up the Raspberry Pi
### Imaging the SD Card:
**IMPORTANT**: This Project uses the RPi OS "Buster", newer OS's have not been confirmed to work.
#### Imaging an SD Card with Raspbian Buster on Windows 10:
* Download Raspbian Buster from the Raspberry Pi Download Site[^1]
  * The version used here is 2021-05-07-raspios-buster-armhf.img
* Unzip the Archived Image
* Insert a blank MicroSD card into your computer
* Use an imaging software to format and image the card
  * The application used to image the card here is Rufus[^2]
  * If the card isn't accessible after the first image, re-image the card.
### Post-Imaging Pre-Boot Setup (Optional Steps):
**All of the following steps should be done within the Boot Folder once the SD card is imaged. None of these steps are required, but they make the first boot of the Pi much simpler**
* Enable SSH by Default
  * Add a plain text file called **SSH**, with no file extension. This file has been provided here in the directory "Files to Add to SD Card Boot Folder Post-Image"
* Manually Connect to Wifi
  * Add a file called **wpa_supplicant.conf**. This file has been provided here in the directory "Files to Add to SD Card Boot Folder Post-Image"
  * Open the file and change "YOUR_NETWORK_NAME" to your wireless network's SSID, and "YOUR_PASSWORD" to your wireless network's password. This setup requires the network you're connecting to, to be using WPA-PSK security.
* Adjust Resolution (If using a remote desktop client)
  * Open the file **config.txt**
  * Uncomment the line ```hdmi_force_hotplug=1```
  * Uncomment the line ```hdmi_group=1```
  * Uncomment the line ```hdmi_mode=1 and change the value to 16```
  * Add the following line to the end of the file ```hdmi_ignore_edid=0xa5000080```
### First Boot Setup:
**All of the following steps are done via command line**
* Assuming the Pi is connected to the network, SSH to it using the default username and password for Raspbian
  * Username: Pi
  * Password: raspberry
* Change the default password using the following command:
  * ```passwd```
* Install Updates
  * ```sudo apt-get update```
  * ```sudo apt-get dist-upgrade``` (This can take up to an hour)
* Enable I2C peripheral
  * Open the Raspbery Pi Config File
    * ```sudo raspi-config```
  * Navigate to Interface Options > I2C
  * Select Yes to enable VNC Server
  * Select Finish
  * Restarting the Pi after this change is recommended. Run this command if not prompted
    * ```sudo shutdown -r```
  * Check that the user-mode I2C interface is now available
    * ````
      pi@sensorhub:~ $ ls /dev/*i2c*
      /dev/i2c-1
      ````
* Install the I2C command line utility programs if they aren't already installed
  * ```sudo apt-get-install -y i2c-tools```
* Install the following python libraries
  * ```pip3 install smbus2```
  * ```pip3 install sparkfun-qwiic```
  * ```pip3 install --upgrade sparkfun-qwiic-tca9548a```
  * ```pip3 install adafruit-circuitpython-ltr390```
  * ```pip3 install adafruit-circuitpython-htu31d```

**Optional Steps**
* Enable VNC Access
  * Open the Raspbery Pi Config File
    * ```sudo raspi-config```
  * Navigate to Interface Options > VNC
  * Select Yes to enable VNC Server
  * Select Finish
* Set Python3 as default
  * Open the .bashrc file
    * ```sudo nano ~/.bashrc```
  * Type the following on a new line at the end of the file
    * ```alias python=python3```
  * Save and exit the file
  * Run the following command to make the alias permanent
    * ```source ~/.bashrc```

## Testing I2C Device Connections on Pi
**The following steps assume a hardware setup identical to the provided schematic**
* Confirm the I2C Mux peripheral is present on the bus. Address 70 show display
  * ````
    pi@sensorhub:~ $ i2cdetect -y 1
         0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:          -- -- -- -- -- -- -- -- -- -- -- -- --
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    70: 70 -- -- -- -- -- -- --
    ````
* Verify Python is setup properly to work with I2C Mux and that all sensors are seen on the bus
  * Run the following enable and disable test scripts for each channel of the MUX a sensor is connected to.
  * Addresses 40 (or 41) and 53 should be listed after each channel is enabled.
    * ````
      pi@sensorhub:~/Downloads $ python i2c_test_enable.py
      Which Channel should be Enabled? (0-7): 0
      Channel 0: Enabled
      Channel 1: Disabled
      Channel 2: Disabled
      Channel 3: Disabled
      Channel 4: Disabled
      Channel 5: Disabled
      Channel 6: Disabled
      Channel 7: Disabled
      pi@sensorhub:~/Downloads $ i2cdetect -y 1
           0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
      00:          -- -- -- -- -- -- -- -- -- -- -- -- --
      10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
      20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
      30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
      40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
      50: -- -- -- 53 -- -- -- -- -- -- -- -- -- -- -- --
      60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
      70: 70 -- -- -- -- -- -- --
      pi@sensorhub:~/Downloads $ python i2c_test_disable.py
      Channel 0: Disabled
      Channel 1: Disabled
      Channel 2: Disabled
      Channel 3: Disabled
      Channel 4: Disabled
      Channel 5: Disabled
      Channel 6: Disabled
      Channel 7: Disabled
      pi@sensorhub:~/Downloads $ i2cdetect -y 1
           0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
      00:          -- -- -- -- -- -- -- -- -- -- -- -- --
      10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
      20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
      30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
      40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
      50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
      60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
      70: 70 -- -- -- -- -- -- --
      ````
* Verify UV Sensor is communicating properly over I2C connection for each MUX channel a sensor is connected to
  * ````
    pi@sensorhub:~/Downloads $ python i2c_test_enable.py
    Which Channel should be Enabled? (0-7): 3
    Channel 0: Disabled
    Channel 1: Disabled
    Channel 2: Disabled
    Channel 3: Enabled
    Channel 4: Disabled
    Channel 5: Disabled
    Channel 6: Disabled
    Channel 7: Disabled
    pi@sensorhub:~/Downloads $ python ltr390_test.py
    UV: 0           Ambient Light: 401
    UVI: 0.0                Lux: 320.8
    UV: 0           Ambient Light: 401
    UVI: 0.0                Lux: 320.8
    UV: 0           Ambient Light: 401
    UVI: 0.0                Lux: 320.8
    UV: 0           Ambient Light: 401
    UVI: 0.0                Lux: 320.8
    UV: 0           Ambient Light: 401
    UVI: 0.0                Lux: 320.8
    UV: 0           Ambient Light: 401
    UVI: 0.0                Lux: 320.8
    <Ctrl+C to Exit>
    pi@sensorhub:~/Downloads $ python i2c_test_disable.py
    Channel 0: Disabled
    Channel 1: Disabled
    Channel 2: Disabled
    Channel 3: Disabled
    Channel 4: Disabled
    Channel 5: Disabled
    Channel 6: Disabled
    Channel 7: Disabled
    ````
* Verify Temperature and Humidity Sensor is communicating properly over I2C connection for each MUX channel a sensor is connected to
  * ````
    pi@sensorhub:~/Downloads $ python i2c_test_enable.py
    Which Channel should be Enabled? (0-7): 0
    Channel 0: Enabled
    Channel 1: Disabled
    Channel 2: Disabled
    Channel 3: Disabled
    Channel 4: Disabled
    Channel 5: Disabled
    Channel 6: Disabled
    Channel 7: Disabled
    pi@sensorhub:~/Downloads $ python htu31_test.py
    Heater is on? True
    Heater is on? False
    Temperature: 15.8 C
    Humidity: 48.3 %

    Temperature: 15.7 C
    Humidity: 48.3 %

    Temperature: 15.8 C
    Humidity: 48.3 %
    <Ctrl+C to Exit>
    pi@sensorhub:~/Downloads $ python i2c_test_disable.py
    Channel 0: Disabled
    Channel 1: Disabled
    Channel 2: Disabled
    Channel 3: Disabled
    Channel 4: Disabled
    Channel 5: Disabled
    Channel 6: Disabled
    Channel 7: Disabled
    ````

## Running the Application

**IMPORTANT**: The I2C Mux Breakout Board must be connected to the raspberry pi before running this application.

* Navigate to the directory with the sensor_fusion.py script.
* Run the following command
  * ```python3 sensor_fusion.py```
* If debug mode is enabled (debug = 1), then the results of the sensor readings, the output of Marzullo's Algorithm on those readings, as well as text indicators on which LED alerts have been triggered, will print to the terminal.
* Additionally, if one doesn't already exist, a new log file will be created for that day. A new log file will be created each day that the script is run.
* Use Ctrl + C to exit the application.

[^1]: https://downloads.raspberrypi.org/raspios_armhf/images/
[^2]: https://rufus.ie/en/
[^3]: https://optoelectronics.liteon.com/upload/download/DS86-2015-0004/LTR-390UV_Final_%20DS_V1%201.pdf
[^4]: https://www.artic.edu/library/discover-our-collections/research-guides/appraisal-and-preservation-resources-for-books
[^5]: https://ccaha.org/resources/light-exposure-artifacts-exhibition
