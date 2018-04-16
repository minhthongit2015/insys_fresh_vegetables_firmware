# coding=utf-8

from core.models.equipment.base_equip.gpio import GPIOPin
from core.modules.thread_looping import ThreadLooping
import random


class Sensor():
  def __init__(self, name="", serial_port=None, owner_station=None, precision=2, emulate_sensors=False):
    self.name = name
    self.serial_port = serial_port
    self.owner_station = owner_station
    self.precision = precision
    self.default = None
    self.last_result = self.random if emulate_sensors else self.default
    self.is_normally = None
    self.min_result_freq_time = 10
    self.emulate_sensors = emulate_sensors
  
  def attach_serial_port(self, serial_port):
    self.serial_port = serial_port
  
  def set_owner_station(self, station):
    self.owner_station = station

  def read(self):
    if self.serial_port:
      self.serial_port.read(self.owner_station, self)

  @property
  def random(self):
    return random.randint(0, 100)

  @property
  def value(self):
    return self.last_result
  @value.setter
  def value(self, val):
    self._last_result = val

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
        print("[Sensor:{}] > {} module is not working normally.".format(self.owner_station.id, self.name))
        self.is_normally = False
        self.on_broken()
        self.on_state_change(self, False)
    else:
      if not self.is_normally or self.is_normally is None:
        print("[Sensor:{}] > {} module is working normally.".format(self.owner_station.id, self.name))
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