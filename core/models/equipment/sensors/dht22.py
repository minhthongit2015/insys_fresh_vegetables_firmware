
from core.models.equipment.base_equip.sensor import Sensor
import random

class DHT22(Sensor):
  def __init__(self, serial_port=None, owner_station=None, emulate_sensors=False):
    super().__init__("dht22", serial_port, owner_station=owner_station, emulate_sensors=emulate_sensors)
    self._temperature = self._humidity = self.random if emulate_sensors else None
    self.emulate_sensors = emulate_sensors

  @property
  def random(self):
    return (round(random.uniform(55,90),self.precision), round(random.uniform(25,32),self.precision))

  @property
  def value(self):
    return (self.temperature, self.humidity)

  @value.setter
  def value(self, val):
    self.temperature = val[0]
    self.humidity = val[1]

  @property
  def temperature(self):
    return self._temperature
  @temperature.setter
  def temperature(self, val):
    self._temperature = val
  
  @property
  def humidity(self):
    return self._humidity
  @humidity.setter
  def humidity(self, val):
    self._humidity = val