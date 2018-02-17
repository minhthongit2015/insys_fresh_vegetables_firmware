
from core.models.plant.user_plant import ListUserPlant
from core.models.equipment.equipment_mgr import EquipmentSet
from core.modules.config_mgr import ConfigManager

import json

import threading
from time import time, sleep

class Hydroponic:
  def __init__(self, info, plant_lib, equipment_set, config_file_path=''):
    self.name = info['name']
    self.id = info['id']
    self.list_user_plant = ListUserPlant(info['plants'], plant_lib)
    self.equipment_set = equipment_set
    self.equipment_set.automation_led.addEventListener("on", self.start_ensure_living_environment)
    self.equipment_set.automation_led.addEventListener("off", self.stop_ensure_living_environment)
    if config_file_path: self.cylinder_cfg = ConfigManager(self.id, config_file_path)
    else: self.cylinder_cfg = None
    self.equipment_set.load_state(self.cylinder_cfg)
  
  def start_ensure_living_environment(self, reason=''):
    print("[{}:{}] > Start ensure living environment.".format(self.id, self.name), flush=True)
    for user_plant in self.list_user_plant.plants:
      for env in user_plant.current_living_environment:
        env.start_ensure_living_environment(self.equipment_set, user_plant)
  
  def stop_ensure_living_environment(self, reason=''):
    print("[{}:{}] > Stop ensure living environment.".format(self.id, self.name), flush=True)
    for user_plant in self.list_user_plant.plants:
      for env in user_plant.current_living_environment:
        env.stop_ensure_living_environment()

  def set_state(self, equipment, state, reason):
    self.equipment_set.set_state(equipment, state, reason, self.cylinder_cfg)

  def dump(self):
    hydroponic_cylinder = {
      "name": self.name,
      "id": self.id,
      "equipment_set": self.equipment_set.dump(),
      "plants": self.list_user_plant.dump()
    }
    return hydroponic_cylinder

class HydroponicManager:
  def __init__(self, plant_lib, equipment_mgr, hydroponic_file_path='./assets/hydroponics.json', config_file_path='./configs/hydroponics.cfg'):
    self.hydroponic_file_path = hydroponic_file_path
    with open(hydroponic_file_path, 'r', encoding='utf-8') as fp:
      hydroponics = json.load(fp)
    
    self.hydroponics = []
    for hydroponic in hydroponics:
      equipment_set = equipment_mgr.get_by_name(hydroponic['id'])
      self.hydroponics.append(Hydroponic(hydroponic, plant_lib, equipment_set, config_file_path))

  def start_ensure_living_environment(self):
    for hydroponic_cylinder in self.hydroponics:
      hydroponic_cylinder.start_ensure_living_environment()
  
  def stop_ensure_living_environment(self):
    for hydroponic_cylinder in self.hydroponics:
      hydroponic_cylinder.stop_ensure_living_environment()
  
  def get_hydroponic_by_name(self, name):
    for hydroponic_cylinder in self.hydroponics:
      if hydroponic_cylinder.name == name:
        return hydroponic_cylinder
    return None

  def get_hydroponic_by_id(self, id):
    for hydroponic_cylinder in self.hydroponics:
      if hydroponic_cylinder.id == id:
        return hydroponic_cylinder
    return None
  
  def set_state(self, cylinder_id, equipment, mode, reason):
    cylinder = self.get_hydroponic_by_id(cylinder_id)
    cylinder.set_state(equipment, mode, reason)
  
  def dump(self):
    hydroponics = []
    for hydroponic_cylinder in self.hydroponics:
      hydroponics.append(hydroponic_cylinder.dump())
    return hydroponics

  # def save(self):
  #   with open(self.hydroponic_file_path, 'w', encoding='utf-8') as fp:
  #     fp.write(str(self.plants))

