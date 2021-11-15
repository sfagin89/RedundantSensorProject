# Enables Channels 0, 3, and 7 on Mux.
# Channels are left Enabled after script ends.

import time                         # Time access and conversion package
import qwiic                    # I2C bus driver package

#The name of this device
_DEFAULT_NAME = "Qwiic Mux"
_AVAILABLE_I2C_ADDRESS = [*range(0x70,0x77 + 1)]

# Which Channel should be enabled?
chan = input("Which Channel should be Enabled? (0-7): ")
# Instantiates an object for the MUX
test = qwiic.QwiicTCA9548A()

# Disable all channels
test.disable_all()

# Enable Channels 0 3, 7
# test.enable_channels([0,3,7])
test.enable_channels(int(chan))

# List Channel Configuration
test.list_channels()
