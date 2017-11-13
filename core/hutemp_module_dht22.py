# coding=utf-8

try: import Adafruit_DHT
except: import core.Adafruit_DHT as Adafruit_DHT

from time import sleep
from datetime import datetime
from core.pins import Pin

class DHT22(Pin):
  def __init__(self, pin, precision=2):
    Pin.__init__(self, pin, False)
    self.sensor = Adafruit_DHT.DHT22
    self.precision = precision

  @property
  def value(self):
    humidity, temperature = Adafruit_DHT.read(self.sensor, self.pin)
    retry = 1
    while humidity is None or temperature is None or humidity > 100 or humidity < 0:
      print("[WARNING] > Hutemp module is failed to read. Retrying! (%d)" % retry)
      retry += 1
      humidity, temperature = Adafruit_DHT.read(self.sensor, self.pin)
      sleep(1)
      if retry > 5: return (80, 20)
    return (round(humidity,self.precision), round(temperature,self.precision))

  def read(self):
    return self.value