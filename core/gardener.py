
from core.models.plant.plant_library import PlantLibrary
from core.models.equipment.hydroponic_mgr import HydroponicManager
from core.modules.config_mgr import ConfigManager

import threading
from time import sleep

class Gardener:
  def __init__(self, equipment_mgr, plant_lib_path='./assets/plant_lib.json'):
    self.cfg = ConfigManager('Gardener')
    self.plant_lib = PlantLibrary(plant_lib_path)
    auto = self.auto
    for equipment_set in equipment_mgr.equipment_sets:
      equipment_set.automation_led.turn(auto)
      equipment_set.hardware_check_led.turn(equipment_set.sensors_mgr.state)
    self.hydroponic_mgr = HydroponicManager(self.plant_lib, equipment_mgr)

  @property
  def auto(self):
    return self.cfg.getz('automation')

  @auto.setter
  def auto(self, state):
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
    self.hydroponic_mgr.start_ensure_living_environment()

  def keep_working(self):
    print("[Gardener] >> Keep working.")
    while True:
      sleep(1)
  
  def stop_working(self):
    print("[Gardener] >> Stop working.")
    try: self.working_thread.join()
    except: pass
    
    self.hydroponic_mgr.stop_ensure_living_environment()

  def command_handle(self, cylinder_name, equipment, state):
    hydroponic_cylinder = self.hydroponic_mgr.get_hydroponic_by_name(cylinder_name)
    if equipment is 'pump':
      hydroponic_cylinder.equipment_set.pump.turn('UserSet', state)

  def dump(self):
    return self.hydroponic_mgr.dump()