
try: import smbus
except: import dummy.smbus as smbus
import struct
import datetime
from time import time

class SEN0161:
  def __init__(self, address=0x04, bus=1, retry=0):
    self.address = address
    self.bus = smbus.SMBus(bus)
    self.errorSignal = -1
    self.last_result = self.errorSignal
    self.last_result_time = 0
    self.min_result_freq_time = 4
    self.retry = retry
  
  @property
  def value(self):
    if time() - self.last_result_time < self.min_result_freq_time:
      return self.last_result
    try:
      block = self.bus.read_i2c_block_data(self.address, 0, 4)
    except Exception as e:
      print("[ERROR] > Unable to detect I2C device on address {}.".format(self.address), flush=True)
      print(e)
      print('-------------- {} --------------'.format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
      return self.errorSignal
    pH = struct.unpack('f', bytearray(block))[0]
    self.last_result = pH
    self.last_result_time = time()
    return pH

  def read(self):
    return self.value

  def check(self):
    if self.value == self.errorSignal:
      print("[pHMeter] >> pHMeter module is failed to read.")
      return False
    else:
      print("[pHMeter] >> pHMeter module is working normally.")
      return True