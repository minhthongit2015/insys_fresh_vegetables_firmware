
from core.modules.thread_looping import ThreadLooping

try: import smbus
except: import dummy.smbus as smbus
import struct
import datetime
from time import time, sleep
import threading
import random

class SEN0161:
  def __init__(self, address=0x04, bus=1, retry=0, precision=3, simulator=False):
    self.name = "pH_Meter"
    self.address = address
    self.bus = smbus.SMBus(bus)
    self.precision = precision
    self.error_signal = -1
    self.last_result = self.error_signal
    self.is_normally = None
    self.min_result_freq_time = 4
    self.simulator = simulator
  
  @property
  def value(self):
    return self.last_result

  @property
  def random(self):
    return round(random.uniform(5,7), self.precision)

  def read(self):
    try:
      block = self.bus.read_i2c_block_data(self.address, 0, 4)
    except Exception as e:
      if self.is_normally or self.is_normally is None:
        if not self.simulator:
          print("[pHMeter] > Unable to detect device on I2C address: {}.".format(self.address), flush=True)
          self.last_result = self.error_signal
        else:
          self.last_result = self.random
      return self.last_result
    pH = round(struct.unpack('f', bytearray(block))[0], self.precision)
    self.last_result = pH
    return pH

  def run(self):
    self.reading_thread = ThreadLooping(target=self.read)
    self.reading_thread.start()
    self.checking_thread = ThreadLooping(target=self.check)
    self.checking_thread.start()
  
  def stop(self):
    self.reading_thread.stop()
    self.checking_thread.stop()

  def check(self):
    if self.value == self.error_signal:
      if self.is_normally or self.is_normally is None:
        print("[pHMeter] > pHMeter module is failed to read.")
        self.is_normally = False
        self.on_broken()
        self.on_state_change(self, False)
    else:
      if not self.is_normally or self.is_normally is None:
        print("[pHMeter] > pHMeter module is working normally.")
        self.is_normally = True
        self.on_working()
        self.on_state_change(self, True)
    sleep(self.min_result_freq_time)

  def on_broken(self):
    """override to add event listener for broken event"""
    pass

  def on_working(self):
    """override to add event listener for working well event"""
    pass
  
  def on_state_change(self, sensor, state):
    """override to add event listener for both working well and broken event"""
    pass