
# from core.models.environment.sensors.hutemp_module_dht22 import DHT22
# from core.models.environment.sensors.phmeter_sen0161 import SEN0161

from core.models.equipment.sensors.dht22 import DHT22
from core.models.equipment.sensors.sen0161 import SEN0161

import random

class SensorsManager:
  def __init__(self, serial_port=None, owner_station=None, emulate_sensors=False):
    self.pHSensor = SEN0161(serial_port=serial_port, owner_station=owner_station)
    self.pHSensor.on_state_change = self.on_state_change
    self.hutempSensor = DHT22(serial_port=serial_port, owner_station=owner_station)
    self.hutempSensor.on_state_change = self.on_state_change

    self.listeners = []
    self.emulate_sensors = emulate_sensors
  
  def run(self):
    self.pHSensor.run()
    self.hutempSensor.run()

  def attach_serial_port(self, serial_port):
    self.serial_port = serial_port
    self.pHSensor.attach_serial_port(serial_port)
    self.hutempSensor.attach_serial_port(serial_port)

  @property
  def state(self):
    if self.hutempSensor.is_normally is None: return None
    return self.hutempSensor.is_normally

  def on_state_change(self, sensor, state):
    for listener in self.listeners:
      listener(self.state)
  
  def add_state_change_listener(self, listener):
    self.listeners.append(listener)

  @property
  def pH(self):
    return self.pHSensor.value

  @property
  def humidity(self):
    return self.hutempSensor.value[0]

  @property
  def temperature(self):
    return self.hutempSensor.value[1]

  @property
  def ppm(self):
    return random.randint(500, 2500)
  
  @property
  def light(self):
    return random.randint(100, 1000)

  def __str__(self):
    return "[{},{},{}]".format(self.pH, self.temperature, self.humidity)

  def dump(self):
    sensor_mgr = {
      "temperature": self.temperature,
      "humidity": self.humidity,
      "light": self.light,
      "ppm": self.ppm,
      "pH": self.pH
    }
    return sensor_mgr