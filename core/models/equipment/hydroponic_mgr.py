
from core.models.plant.user_plant import ListUserPlant
import json

import threading
from time import time, sleep

class Hydroponic:
  def __init__(self, info, plant_lib, equipment_set):
    self.name = info['name']
    self.list_user_plant = ListUserPlant(info['plants'], plant_lib)
    self.equipment_set = equipment_set
  
  def start_ensure_living_environment(self):
    for user_plant in self.list_user_plant.plants:
      for env in user_plant.current_living_environment:
        env.start_ensure_living_environment(self.equipment_set, user_plant)
  
  def stop_ensure_living_environment(self):
    for user_plant in self.list_user_plant.plants:
      for env in user_plant.current_living_environment:
        env.stop_ensure_living_environment()

  def dump(self):
    hydroponic_cylinder = {
      "name": self.name,
      "equipment_set": self.equipment_set.dump(),
      "plants": self.list_user_plant.dump()
    }
    return hydroponic_cylinder

class HydroponicManager:
  def __init__(self, plant_lib, equipment_mgr, hydroponic_file_path='./assets/hydroponics.json'):
    self.hydroponic_file_path = hydroponic_file_path
    with open(hydroponic_file_path, 'r', encoding='utf-8') as fp:
      hydroponics = json.load(fp)
    
    self.hydroponics = []
    for hydroponic in hydroponics:
      equipment_set = equipment_mgr.get_by_name(hydroponic['equipment_set_name'])
      self.hydroponics.append(Hydroponic(hydroponic, plant_lib, equipment_set))

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
  
  def dump(self):
    hydroponics = []
    for hydroponic_cylinder in self.hydroponics:
      hydroponics.append(hydroponic_cylinder.dump())
    return hydroponics

  # def save(self):
  #   with open(self.hydroponic_file_path, 'w', encoding='utf-8') as fp:
  #     fp.write(str(self.plants))

