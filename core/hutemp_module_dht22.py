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
    humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
    while humidity is None or temperature is None or humidity > 100 or humidity < 0:
      humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
    return (round(humidity,self.precision), round(temperature,self.precision))

  def read(self):
    return self.value