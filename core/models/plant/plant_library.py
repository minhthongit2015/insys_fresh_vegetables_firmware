# -*- coding: utf-8 -*-

"""
## Quản lý thư viện chăm sóc cây trồng
+ 1 ``ListPlant`` có nhiều ``Plant``
+ 1 ``Plant`` có nhiều ``GrowthStage``
+ 1 ``GrowthStage`` có nhiều ``WaterPoints``
+ 1 ``WaterPoints`` có nhiều ``WaterTime``
____________________________________

`Cho giai đoạn hiện tại:
 - Mỗi bộ xử lý trung tâm sẽ quản lý nhiều trụ.
 - Mỗi trụ sẽ có pin khác nhau (các pin được cấp tự động).
   + pin máy bơm nước.
   + pin van dinh dưỡng.
 - Trên mỗi trụ sẽ có thêm các đèn báo hiệu riêng.
   + đèn báo tình trạng hoạt động.
   + đèn báo tình trạng môi trường.
   + đèn báo chế độ hoạt động
 - Dành riêng 5 GPIO cho đèn báo tại bộ xử lý trung tâm (bảng mạch chính).
`

"""

from core.models.plant.plant import Plant
from core.models.plant.growth_stage import GrowthStage
from core.models.environment.environment_factors import *
from core.models.environment.living_environment import LivingEnviroment

import json

class PlantLibrary:
  def __init__(self, plant_lib_path):
    self.load(plant_lib_path)
  
  def load(self, plant_lib_path):
    try:
      with open(plant_lib_path, 'r', encoding='utf-8') as fp:
        self.library = json.load(fp, encoding="utf-8")
      print("[PLANTLIB] >> Plant library loaded.")
      self.parse_library(self.library)
      print("[PLANTLIB] >> Plant library parsed.")
    except:
      print("[PLANTLIB] >> Failed to load plant library ({})".format(plant_lib_path))

  def parse_library(self, library):
    self.plant_lib = []
    for plant in self.library:
      self.plant_lib.append(PlantLibrary.parse_plant(plant))

  @staticmethod
  def parse_plant(plant_in_lib):
    growth_stages = []
    for stage in plant_in_lib['growth_stages']:
      env_factors = []
      for env in stage['living_environment']:
        env_factor = ENV_TYPE_MAPPING[env['name']](env)
        env_factors.append(env_factor)
      growth_stages.append(GrowthStage(stage['stage_order'], stage['stage_name'], (stage['start'], stage['end']), LivingEnviroment(env_factors)))
    return Plant(plant_in_lib['plant_name'], plant_in_lib['plant_type'], growth_stages)