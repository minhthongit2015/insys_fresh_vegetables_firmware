# coding=utf-8

try: import Adafruit_DHT
except: import dummy.Adafruit_DHT as Adafruit_DHT

from time import sleep, time
from datetime import datetime
from core.pins import Pin
import threading

class DHT22(Pin):
  def __init__(self, pin, precision=2, retry=15):
    Pin.__init__(self, pin, False)
    self.sensor = Adafruit_DHT.DHT22
    self.precision = precision
    self.default = (80, 20)
    self.last_result = self.default
    self.retry = retry
    self.is_normally = False
    self.min_result_freq_time = 10

  @property
  def value(self):
    return self.last_result

  def read(self):
    humidity, temperature = Adafruit_DHT.read(self.sensor, self.pin)
    retry = 0
    while humidity is None or temperature is None or humidity > 100 or humidity < 0 or (temperature == 0 and humidity == 0):
      # print("[DHT22] > Hutemp module is failed to read. Retry %d" % retry, flush=True)
      retry += 1
      humidity, temperature = Adafruit_DHT.read(self.sensor, self.pin)
      sleep(2)
      if retry >= self.retry:
        if self.is_normally:
          print("[DHT22] > Hutemp module is failed to read.")
        return self.default
    humidity = 100 if humidity >= 99 else humidity
    hutemp = (round(humidity,self.precision), round(temperature,self.precision))
    self.last_result = hutemp
    return hutemp

  def run(self):
    self.running_thread = threading.Thread(target=self._run)
    self.running_thread.start()
    self.checking_thread = threading.Thread(target=self.check)
    self.checking_thread.start()
  
  def join(self):
    self.running_thread.join()
    self.checking_thread.join()

  def _run(self):
    last_result_time = 0
    while True:
      delta = time() - last_result_time
      if delta < self.min_result_freq_time:
        sleep(self.min_result_freq_time - delta)
      last_result_time = time()
      self.read()

  def check(self):
    while True:
      if self.value == self.default:
        if self.is_normally:
          print("[DHT22] > Hutemp module is failed to read.")
          self.is_normally = False
          self.on_broken()
      else:
        if not self.is_normally:
          print("[DHT22] > Hutemp module is working normally.")
          self.is_normally = True
          self.on_working()
      sleep(self.min_result_freq_time)

  def on_broken(self):
    """override to add event listener for broken event"""
    pass

  def on_working(self):
    """override to add event listener for working good event"""
    pass