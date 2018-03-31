

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
      print("[StationSync] > Emulate station")
    else:
      self.serial.add_message_listener(self.on_message)
    print("[StationSync] >> Stations synchronize handler stated on port {}!".format(self.serial.serial.port))

  def start(self):
    self._running_thread = Thread(target=self._run)
    self._running_thread.start()

  def on_message(self, msg):
    station_id = msg.split("_")[0]
    msg_body = msg[len(station_id)+1 : ]
    if len(msg) == 3: # msg: B01  (Trụ mới khởi động và kết nối đến hệ thống)
      if self.gardener.attach_station(station_id, self):
        pass
    else:
      if msg_body[0] in ['T', 'H']:
        sensor_data = self.resolve_sensor_data(msg_body)
        self.gardener.update_station_sensors(station_id, sensor_data)
      pass
    pass
  
  def resolve_sensor_data(self, sensor_data): # T27.5_H80
    T, H = sensor_data.split("_")
    return { "temperature": float(T[1:]), "humidity": float(H[1:]) }

  # def get_info(self, callback):
  #   self.serial.get("#01I", callback)
  
  # def get_state(self, callback):
  #   self.serial.get("#S", callback)

  def read(self, station, sensor):
    if station is None:
      raise Exception("[StationSync] > Station is None")
    self.serial.send("#{}S".format(station.id))

  def on(self, station, switch):
    self.serial.send("#{}m1".format(station.id))

  def off(self, station, switch):
    self.serial.send("#{}m0".format(station.id))

  def _emulate_station(self, data):
    print("[EmuStation] > {}".format(data))
    station_id = data[1:3]
    if len(data) == 4 and data[3] is 'S': # data = #B1S (Server yêu cầu dữ liệu cảm biến từ máy trạm)
       self.serial.send("#{}_T27.5_H80".format(station_id))