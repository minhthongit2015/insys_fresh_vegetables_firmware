
import smbus
import struct

class SEN0161:
  def __init__(self, address=0x04, bus=1):
    self.address = address
    self.bus = smbus.SMBus(bus)
  
  @property
  def value(self):
    try:
      block = self.bus.read_i2c_block_data(self.address, 0, 4)
    except:
      print("[ERROR] > Unable to detect I2C device on address {}. Please Check your wiring or I2C address".format(self.address))
      return 0
    return struct.unpack('f', bytearray(block))[0]

  def read(self):
    return self.value