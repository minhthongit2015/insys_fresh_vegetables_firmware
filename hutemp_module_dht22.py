# coding=utf-8

import Adafruit_DHT
from time import sleep
from datetime import datetime
from pins import Pin

class DHT22(Pin):
  def __init__(self, pin, precision=2):
    Pin.__init__(self, pin, False)
    self.sensor = Adafruit_DHT.DHT22
    self.precision = precision

  def read(self):
    humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
    while humidity is None or temperature is None or humidity > 100 or humidity < 0:
      humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
    return (round(humidity,self.precision), round(temperature,self.precision))
