# coding=utf-8

from core.models.gpio.gpio import Pin
from core.modules.thread_looping import ThreadLooping

try: import Adafruit_DHT
except: import dummy.Adafruit_DHT as Adafruit_DHT

from time import sleep, time
import random

class DHT22(Pin):
  def __init__(self, pin, precision=2, retry=15, simulator=False):
    super().__init__(pin, False)
    self.name = "HuTemp"
    self.sensor = Adafruit_DHT.DHT22
    self.precision = precision
    self.default = (80, 20)
    self.last_result = self.random # Simulation
    self.retry = retry
    self.is_normally = None
    self.min_result_freq_time = 10
    self.simulator = simulator

  @property
  def value(self):
    return self.last_result

  @property
  def random(self):
    return (round(random.uniform(55,90),self.precision), round(random.uniform(25,32),self.precision))

  def read(self):
    humidity, temperature = Adafruit_DHT.read(self.sensor, self.pin)
    retry = 0
    while humidity is None or temperature is None or humidity > 100 or humidity < 0 or (temperature == 0 and humidity == 0):
      if self.simulator:
        self.last_result = self.random
        return self.last_result
      else:
        retry += 1
        humidity, temperature = Adafruit_DHT.read(self.sensor, self.pin)
        sleep(2)
        if retry >= self.retry:
          if self.is_normally or self.is_normally is None:
            print("[DHT22] > Hutemp module is failed to read.")
          return self.default
    humidity = 100 if humidity >= 99 else humidity
    hutemp = (round(humidity,self.precision), round(temperature,self.precision))
    self.last_result = hutemp
    return hutemp

  def run(self):
    self.reading_thread = ThreadLooping(target=self.read, wait_time=self.min_result_freq_time)
    self.reading_thread.start()
    self.checking_thread = ThreadLooping(target=self.check, wait_time=self.min_result_freq_time)
    self.checking_thread.start()
  
  def stop(self):
    self.reading_thread.stop()
    self.checking_thread.stop()

  def check(self):
    if self.value == self.default:
      if self.is_normally or self.is_normally is None:
        print("[DHT22] > Hutemp module is not working normally.")
        self.is_normally = False
        self.on_broken()
        self.on_state_change(self, False)
    else:
      if not self.is_normally or self.is_normally is None:
        print("[DHT22] > Hutemp module is working normally.")
        self.is_normally = True
        self.on_working()
        self.on_state_change(self, True)

  def on_broken(self):
    """override to add event listener for broken event"""
    pass

  def on_working(self):
    """override to add event listener for working good event"""
    pass

  def on_state_change(self, sensor, state):
    """override to add event listener for both working well and broken event"""
    pass