
from core.models.equipment.base_equip.sensor import Sensor

class SEN0161(Sensor):
  def __init__(self, serial_port=None, owner_station=None):
    super().__init__("sen0161", serial_port, owner_station=owner_station)
