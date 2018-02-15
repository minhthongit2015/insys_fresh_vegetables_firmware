# -*- coding: utf-8 -*-

"""
## Phân lớp module:
+ ``PlantList`` quản lý các ``Plant``
+ ``Plant`` lưu thông tin cây trồng
____________________________________

`Cho giai đoạn hiện tại:
 - Mỗi bộ xử lý trung tâm sẽ quản lý nhiều trụ.
 - Mỗi trụ sẽ có pin khác nhau (các pin được cấp tự động).
   + pin máy bơm nước.
   + pin van dinh dưỡng.
 - Trên mỗi trụ sẽ có thêm các đèn báo hiệu riêng.
   + đèn báo tình trạng hoạt động.
   + đèn báo tình trạng môi trường.
   + đèn báo 
 - Dành riêng 5 GPIO cho đèn báo tại bộ xử lý trung tâm (bảng mạch chính).
`

## Mô tả các module:
**PlantList** - Quản lý danh sách cây trồng
  * 

**Plant** - Quản lý thông tin cơ bản cây trồng
  * Tên cây trồng
  * Các giai đoạn phát triển
"""

import datetime
import json


class UserPlant:
  """ Thông tin cây trồng, nhiều giai đoạn phát triển """
  def __init__(self, alias='', planting_date='', plant_type='', plant_id='', plant_lib=None):
    self.alias = alias
    self.planting_date = planting_date
    self.plant_type = plant_type
    self.plant_id = plant_id
    self.plant = None
    
    day,month,year = planting_date.split('/')
    self.planting_date_obj = datetime.datetime(day=int(day), month=int(month), year=int(year))
    self.attach_plant_lib(plant_lib)

  def attach_plant_lib(self, plant_lib):
    if not plant_lib: return
    for plant in plant_lib:
      if plant.plant_type == self.plant_type:
        self.plant = plant
        break

  @property
  def current_living_environment(self):
    if not self.plant: return None
    return self.current_growth_stage.living_environment.env_factors

  @property
  def current_growth_stage(self):
    start = self.planting_date_obj
    now = datetime.datetime.now()
    daypass = now - start
    for stage in self.plant.growth_stages:
      if stage.start <= daypass.days + 1 <= stage.end:
        return stage
    return None

  def dump(self):
    user_plant = {
      "alias": self.alias,
      "plant_type": self.plant_type,
      "plant_id": self.plant_id,
      "planting_date": self.planting_date
    }
    return user_plant

  @staticmethod
  def normalize(plant, plant_lib):
    return UserPlant( alias = plant['alias'],\
                      planting_date = plant['planting_date'],\
                      plant_type = plant['plant_type'],\
                      plant_id = plant['plant_id'],\
                      plant_lib = plant_lib.plant_lib)


class ListUserPlant:
  """ Quản lý danh sách cây trồng
  #### Thông tin:
  - Tên, loại cây trồng.
  - Điều kiện môi trường thời gian thực.
  - Điều kiện môi trường kỳ vọng.
  """
  def __init__(self, plants, plant_lib):
    self.load(plants, plant_lib)

  def load(self, plants, plant_lib):
    self.plants = []
    for plant in plants:
      self.plants.append(UserPlant.normalize(plant, plant_lib))

  def dump(self):
    plants = []
    for plant in self.plants:
      plants.append(plant.dump())
    return plants

  def save(self, plants_path):
    with open(plants_path, 'w', encoding='utf-8') as fp:
      fp.write(str(self.plants))