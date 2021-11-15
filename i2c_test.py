# Testing I2C

from smbus2 import SMBus

# Open i2c bus 1 and read one byte from address 70, offset 0
with SMBus(1) as bus:
    bus.pec = 1  # Enable PEC
    b = bus.read_byte_data(70, 0)
    print(b)
