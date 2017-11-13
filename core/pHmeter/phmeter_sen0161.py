
import smbus
import struct

class SEN0161:
  def __init__(self, address=0x04, bus=1):
    self.address = address
    self.bus = smbus.SMBus(bus)
  
  @property
  def value(self):
    return struct.unpack('f', bytearray(self.bus.read_i2c_block_data(self.address, 0, 4)))[0]

  def read(self):
    return self.value