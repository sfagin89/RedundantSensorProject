# Disables All Channels on Mux and verifies status
# Channels are all Disabled after script ends.

import time                         # Time access and conversion package
import qwiic                    # I2C bus driver package

#The name of this device
_DEFAULT_NAME = "Qwiic Mux"
_AVAILABLE_I2C_ADDRESS = [*range(0x70,0x77 + 1)]

# Instantiates an object for the MUX
test = qwiic.QwiicTCA9548A()

# Disable all channels
test.disable_all()

# List Channel Configuration
test.list_channels()
