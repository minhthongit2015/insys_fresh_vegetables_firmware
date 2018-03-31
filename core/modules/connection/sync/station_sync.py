

from core.modules.connection.rs485 import RS485
from core.modules.thread_looping import ThreadLooping
from threading import Thread

class StationSync:
  def __init__(self, gardener):
    self.serial = RS485(port=['COM5', '/dev/ttyS0'])
    self.gardener = gardener
    self.send_queue = []
  
  def _run(self):
    self.serial.start()
    if self.serial.serial.port == "/dev/ttyS0":
      self.serial.add_message_listener(self._emulate_station)
    else:
      self.serial.add_message_listener(self.on_message)
    print("[StationSync] >> Stations synchronize handler stated on port {}!".format(self.serial.serial.port))

  def start(self):
    self._running_thread = Thread(target=self._run)
    self._running_thread.start()

  def on_message(self, msg):
    cylinderID = msg[1:3] # 2 ký tự id trụ
    msgBody = msg[3:]
    if len(msg) == 3: # Trụ mới khởi động và kết nối đến hệ thống
      if self.gardener.attach_station(cylinderID, self):
        pass
    else:
      if msgBody[0] in ['T', 'H']:
        self.gardener.update_station_sensors(cylinderID, msgBody)
      pass
    pass

  # def get_info(self, callback):
  #   self.serial.get("#01I", callback)
  
  # def get_state(self, callback):
  #   self.serial.get("#S", callback)
  
  def translate(self, msg):
    pass

  def read(self, station, sensor):
    if station is None:
      raise "[StationSync] > Station is None"
    self.serial.send("#{}S".format(station.id))

  def on(self, station, switch):
    self.serial.send("#{}m1".format(station.id))

  def off(self, station, switch):
    self.serial.send("#{}m0".format(station.id))

  def _emulate_station(self, data):
    print("[StationSync] > {}".format(data))