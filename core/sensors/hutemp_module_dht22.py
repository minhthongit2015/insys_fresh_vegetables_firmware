# coding=utf-8

try: import Adafruit_DHT
except: import dummy.Adafruit_DHT as Adafruit_DHT

from time import sleep, time
from datetime import datetime
from core.pins import Pin

class DHT22(Pin):
  def __init__(self, pin, precision=2, retry=15):
    Pin.__init__(self, pin, False)
    self.sensor = Adafruit_DHT.DHT22
    self.precision = precision
    self.default = (80, 20)
    self.last_result = self.default
    self.last_result_time = 0
    self.min_result_freq_time = 30
    self.retry = retry

  @property
  def value(self):
    if time() - self.last_result_time < self.min_result_freq_time:
      return self.last_result
    humidity, temperature = Adafruit_DHT.read(self.sensor, self.pin)
    retry = 1
    while humidity is None or temperature is None or humidity > 100 or humidity < 0:
      print("[DHT22] > Hutemp module is failed to read. Retry %d" % retry, flush=True)
      retry += 1
      humidity, temperature = Adafruit_DHT.read(self.sensor, self.pin)
      sleep(2)
      if retry > self.retry: return self.default
    hutemp = (round(humidity,self.precision), round(temperature,self.precision))
    self.last_result = hutemp
    self.last_result_time = time()
    return hutemp

  def read(self):
    return self.value

  def check(self):
    if self.value == self.default:
      print("[DHT22] >> Hutemp module is failed to read.")
      return False
    else:
      print("[DHT22] >> Hutemp module is working normally.")
      return True