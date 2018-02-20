
from core.models.plant.plant_library import PlantLibrary
from core.models.equipment.hydroponic_mgr import HydroponicManager
from core.modules.config_mgr import ConfigManager
from core.modules.logger import Logger
from core.modules.thread_looping import ThreadLooping

import threading
from time import sleep, time

class Gardener:
  def __init__(self, equipment_mgr, plant_lib_path='./assets/plant_lib.json'):
    self.cfg = ConfigManager('Gardener')
    self.plant_lib = PlantLibrary(plant_lib_path)
    auto = self.auto
    for equipment_set in equipment_mgr.equipment_sets:
      equipment_set.automation_led.turn(auto)
      equipment_set.hardware_check_led.turn(equipment_set.sensors_mgr.state)
    self.hydroponic_mgr = HydroponicManager(self.plant_lib, equipment_mgr)

    self.logger = Logger()
    self.tracking_wait_time = 300 # second = 5 minutes
    self.tracking_thread = ThreadLooping(self._tracking_handle, self.tracking_wait_time)

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
    self.start_tracking()
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
    
    self.hydroponic_mgr.stop_ensure_living_environment()

  def command_handle(self, cylinder_id, equipment, state):
    self.hydroponic_mgr.set_state(cylinder_id, equipment, state, 'UserSet')
  
  def get_cylinder_info(self, cylinder_id):
    cylinder = self.hydroponic_mgr.get_hydroponic_by_id(cylinder_id)
    return cylinder.dump()

  def _tracking_handle(self):
    for cylinder in self.hydroponic_mgr.hydroponics:
      temperature = cylinder.equipment_set.sensors_mgr.temperature
      humidity = cylinder.equipment_set.sensors_mgr.humidity
      record = "{},{}".format(temperature, humidity)
      Logger.log(record, 'envs', './log/{}'.format(cylinder.id))

  def start_tracking(self):
    self.tracking_thread.start()

  def stop_tracking(self):
    self.tracking_thread.stop()

  def get_records_from(self, cylinder_id, hours_ago=6):
    cylinder = self.hydroponic_mgr.get_hydroponic_by_id(cylinder_id)
    records = Logger.get_log('envs', './log/{}'.format(cylinder.id), hours_ago)
    records_map = []
    for record in records:
      data = record[1].split(',')
      records_map.append([record[0], [float(data[0]), float(data[1])]])
    return records_map

  def plant_new_plant(self, cylinder_id, plant_type, planting_date, alias):
    self.hydroponic_mgr.plant_new_plant(cylinder_id, plant_type, planting_date, alias)

  def remove_plant(self, cylinder_id, plant_id):
    self.hydroponic_mgr.remove_plant(cylinder_id, plant_id)

  def dump(self):
    return self.hydroponic_mgr.dump()