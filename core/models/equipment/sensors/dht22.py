
from core.models.equipment.base_equip.sensor import Sensor

class DHT22(Sensor):
  def __init__(self, serial_port=None, owner_station=None):
    super().__init__("dht22", serial_port, owner_station=owner_station)
