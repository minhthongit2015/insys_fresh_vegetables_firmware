
try: import smbus
except: import dummy.smbus as smbus
import struct
import datetime

class SEN0161:
  def __init__(self, address=0x04, bus=1):
    self.address = address
    self.bus = smbus.SMBus(bus)
    self.errorSignal = -1
  
  @property
  def value(self):
    try:
      block = self.bus.read_i2c_block_data(self.address, 0, 4)
    except Exception as e:
      print("[ERROR] > Unable to detect I2C device on address {}. Please Check your wiring or I2C address".format(self.address), flush=True)
      print(e)
      print('-------------- {} --------------'.format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
      return self.errorSignal
    return struct.unpack('f', bytearray(block))[0]

  def read(self):
    return self.value

  def check(self):
    if self.value == self.errorSignal:
      print("[pHMeter] >> pHMeter module is failed to read.")
      return False
    else:
      print("[pHMeter] >> pHMeter module is working normally.")
      return True