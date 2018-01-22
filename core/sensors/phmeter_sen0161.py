
try: import smbus
except: import dummy.smbus as smbus
import struct
import datetime
from time import time, sleep
import threading
import random

class SEN0161:
  def __init__(self, address=0x04, bus=1, retry=0, precision=3):
    self.address = address
    self.bus = smbus.SMBus(bus)
    self.precision = precision
    self.error_signal = -1
    self.last_result = self.error_signal
    self.is_normally = None
    self.min_result_freq_time = 4
  
  @property
  def value(self):
    return self.last_result

  @property
  def random(self):
    return round(random.uniform(5,7),self.precision)

  def read(self):
    try:
      block = self.bus.read_i2c_block_data(self.address, 0, 4)
    except Exception as e:
      if self.is_normally or self.is_normally is None:
        print("[pHMeter] > Unable to detect device on I2C address: {}.".format(self.address), flush=True)
      self.last_result = self.random
      return self.last_result
      # return self.error_signal
    pH = round(struct.unpack('f', bytearray(block))[0], self.precision)
    self.last_result = pH
    return pH

  def _run(self):
    last_result_time = 0
    while True:
      delta = time() - last_result_time
      if delta < self.min_result_freq_time:
        sleep(self.min_result_freq_time - delta)
      last_result_time = time()
      self.read()

  def run(self):
    self.running_thread = threading.Thread(target=self._run)
    self.running_thread.start()
    self.checking_thread = threading.Thread(target=self.check)
    self.checking_thread.start()
  
  def join(self):
    self.running_thread.join()
    self.checking_thread.join()

  def check(self):
    while True:
      if self.value == self.error_signal:
        if self.is_normally or self.is_normally is None:
          print("[pHMeter] > pHMeter module is failed to read.")
          self.is_normally = False
          self.on_broken()
      else:
        if not self.is_normally or self.is_normally is None:
          print("[pHMeter] > pHMeter module is working normally.")
          self.on_working()
          self.is_normally = True
      sleep(self.min_result_freq_time)

  def on_broken(self):
    """override to add event listener for broken event"""
    pass

  def on_working(self):
    """override to add event listener for working good event"""
    pass