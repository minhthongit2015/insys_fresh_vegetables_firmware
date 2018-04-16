

from core.modules.connection.rs485 import RS485
from core.modules.thread_looping import ThreadLooping
from threading import Thread

class StationSync:
  def __init__(self, gardener):
    self.serial = RS485(port=['COM5','COM6','COM7', '/dev/ttyS0'])
    self.gardener = gardener
    self.send_queue = []
  
  def _run(self):
    self.serial.start()
    if False and self.serial.serial.port == "/dev/ttyS0":
      self.serial.add_message_listener(self._emulate_station)
      print("[StationSync] > Emulate station")
    else:
      self.serial.add_message_listener(self.on_message)
    print("[StationSync] >> Stations synchronize handler stated on port {}".format(self.serial.serial.port))

    # Yêu cầu tất cả các trạm gửi thông tin của mình về trung tâm
    self.handshake_session()

  def handshake_session(self):
    self.serial.send("GETALL")

  def start(self):
    self._running_thread = Thread(target=self._run)
    self._running_thread.start()

  def on_message(self, msg):
    part = msg.split("_")
    msgType = part[0]
    station_id = part[1]
    msg_body = part[2:]

    if msgType is 'I': # Trạm kết nối đến trung tâm
      if self.gardener.attach_station(station_id, self):
        pass
      self.serial.send("A_{}".format(station_id))
    if msgType is 'S':
      try:
        sensor_data = self.resolve_sensor_data(msg_body)
        self.gardener.update_station_sensors(station_id, sensor_data)
      except:
        pass

  def resolve_sensor_data(self, sensor_data): # T27.5_H80
    T, H = sensor_data
    return { "temperature": float(T[1:]), "humidity": float(H[1:]) }

  # def get_info(self, callback):
  #   self.serial.get("#01I", callback)
  
  # def get_state(self, callback):
  #   self.serial.get("#S", callback)

  def read(self, station, sensor):
    if station is None:
      raise Exception("[StationSync] > Station is None")
    self.serial.send("S_{}".format(station.id))

  def on(self, station, switch):
    if switch.name in ['Water']:
      self.serial.send("C_{}_M1".format(station.id))
    elif switch.name in ['Rotate']:
      self.serial.send("C_{}_R1".format(station.id))
    elif switch.name in ['Light']:
      self.serial.send("C_{}_L1".format(station.id))

  def off(self, station, switch):
    if switch.name in ['Water']:
      self.serial.send("C_{}_M0".format(station.id))
    elif switch.name in ['Rotate']:
      self.serial.send("C_{}_R0".format(station.id))
    elif switch.name in ['Light']:
      self.serial.send("C_{}_L0".format(station.id))

  def _emulate_station(self, msg):
    print("[EmuStation] > {}".format(msg))
    station_id = msg.split("_")[0]
    msg_body = msg[len(station_id)+1 : ]
    temp, humi = self.gardener.station_mgr.stations[0].equipment_set.sensors_mgr.hutempSensor.random
    if msg == station_id + '_S': # data: B1_S (Server yêu cầu dữ liệu cảm biến từ máy trạm)
      sensor_data = "{}_T{}_H{}".format(station_id, temp, humi)
      self.serial.send(sensor_data)
      print('[EmuStation] > send: {}'.format(sensor_data))