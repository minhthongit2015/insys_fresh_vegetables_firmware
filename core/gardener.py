
from core.models.plant.plant_library import PlantLibrary
from core.models.equipment.station_mgr import StationManager
from core.modules.config_mgr import ConfigManager
from core.modules.logger import Logger
from core.modules.thread_looping import ThreadLooping

import threading
from time import sleep, time

class Gardener:
  def __init__(self, plant_lib_path='./assets/plant_lib.json'):
    self.cfg = ConfigManager('Gardener')
    self.plant_lib = PlantLibrary(plant_lib_path)
    self.station_mgr = StationManager(self.plant_lib)

    self.logger = Logger()
    self.logging = 300 # second = 5 minutes
    self.logging_thread = ThreadLooping(self._logging_handle, self.logging)

  @property
  def auto(self):
    return self.cfg.getz('automation')

  @auto.setter
  def auto(self, state):
    print("[Gardener] > Automation mode is set to {}".format(state))
    self.cfg.set('automation', state)

  def start_working(self):
    print("[Gardener] >> Start working!")
    if self.auto:
      print("[Gardener] > Automation mode is on.")
      self.working_thread = threading.Thread(target=self._work)
      self.working_thread.start()
    else:
      print("[Gardener] > Automation mode is off.")

  def _work(self):
    # self.hydroponic_mgr.start_ensure_living_environment()
    self.station_mgr.run()
    self.start_logging()
    pass

  def keep_working(self):
    print("[Gardener] >> Keep working.")
    while True:
      sleep(1)
  
  def stop_working(self):
    print("[Gardener] >> Stop working.")
    try: self.working_thread.join()
    except: pass
    self.stop_tracking()
    
    self.station_mgr.stop_ensure_living_environment()

  def command_handle(self, station_id, equipment, state):
    self.station_mgr.set_state(station_id, equipment, state, 'UserSet')
  
  def get_station_info(self, station_id):
    station = self.station_mgr.get_station_by_id(station_id)
    return station.dump()

  def _logging_handle(self):
    for station in self.station_mgr.stations:
      temperature = station.equipment_set.sensors_mgr.temperature
      humidity = station.equipment_set.sensors_mgr.humidity
      record = "{},{}".format(temperature, humidity)
      Logger.log(record, 'envs', './log/{}'.format(station.id))

  def start_logging(self):
    self.logging_thread.start()

  def stop_tracking(self):
    self.logging_thread.stop()

  def get_records_from(self, station_id, hours_ago=6):
    station = self.station_mgr.get_station_by_id(station_id)
    records = Logger.get_log('envs', './log/{}'.format(station.id), hours_ago)
    records_map = []
    for record in records:
      data = record[1].split(',')
      records_map.append([record[0], [float(data[0]), float(data[1])]])
    return records_map

  def plant_new_plant(self, station_id, plant_type, planting_date, alias):
    self.station_mgr.plant_new_plant(station_id, plant_type, planting_date, alias)

  def remove_plant(self, station_id, plant_id):
    self.station_mgr.remove_plant(station_id, plant_id)

  def attach_station(self, station_id, serial_port):
    self.station_mgr.attach_station(station_id, serial_port)

  def attach_serial_port(self, serial_port):
    self.station_mgr.attach_serial_port(serial_port)

  def update_station_sensors(self, station_id, sensors_data):
    pass
