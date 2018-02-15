
from core.modules.timepoint import TimePointGroup
from core.modules.logger import Logger

from time import time, sleep
import threading

class EnvironmentFactor:
  def __init__(self, name, info_in_lib=None):
    self.name = name
    self.is_ensure_living_environment = False
    # self.parse_from_lib(info_in_lib)

  def parse_from_lib(self, info_in_lib):
    pass

  def _ensure_living_environment_loop(self):
    while self.is_ensure_living_environment:
      self._ensure_living_environment()
      sleep(2)

  def _ensure_living_environment(self):
    """ Kiểm tra thông số môi trường có hợp lệ và đưa ra hành động cần thiết để điều chỉnh
    #### Một số tham số ẩn:
     - ``self``.**equipment_set**: Đối tượng quản lý trang thiết bị (cảm biến, van, bơm...)
     - ``self``.**user_plant**: Đối tượng lưu thông tin cây trồng (ngày trồng và thông tin liên kết từ plant library)
    """
    pass
  
  def _save_equipmentset_plantinfo(self, equipment_set, user_plant):
    self.equipment_set = equipment_set
    self.user_plant = user_plant

  def start_ensure_living_environment(self, equipment_set=None, user_plant=None):
    if equipment_set is not None and user_plant is not None:
      self._save_equipmentset_plantinfo(equipment_set, user_plant)
    if self.equipment_set is not None and self.user_plant is not None:
      self.is_ensure_living_environment = True
      self.ensure_thread = threading.Thread(target=self._ensure_living_environment_loop)
      self.ensure_thread.start()
    else:
      print("[EnvFactor] > equipment_set or user_plant is None")
  
  def stop_ensure_living_environment(self, callback=None):
    self.is_ensure_living_environment = False
    self.ensure_thread.join()
    if callback: callback()

  def restart(self):
    self.stop_ensure_living_environment(self.start_ensure_living_environment)

class WaterCondition(EnvironmentFactor):
  def __init__(self, info_in_lib):
    super().__init__('Water')
    self.water_points = []
    self.parse_from_lib(info_in_lib)

  def parse_from_lib(self, info_in_lib):
    self.water_points = []
    for water in info_in_lib['water']:
      if 'duration' not in water:
        water['duration'] = '15'  # default is water for 15 minutes
      if 'every' in water:
        self.water_points.append(TimePointGroup(every=water['every'], duration=water['duration']))
      elif 'time' in water:
        self.water_points.append(TimePointGroup(water['time'], water['duration']))

  def _ensure_living_environment(self):
    for t in self.water_points:
      if t.is_time_for_action(self.user_plant.planting_date_obj):
        if self.equipment_set.pump.start('timing'):
          print("[EnvFactor] > Start watering by time: {}".format(Logger.time()))
        break
    else:
      if self.equipment_set.pump.stop('timing'):
        print("[EnvFactor] > Stop watering by time: {}".format(Logger.time()))

class TemperatureCondition(EnvironmentFactor):
  def __init__(self, info_in_lib):
    super().__init__('Temperature')
    self.parse_from_lib(info_in_lib)
  
  def parse_from_lib(self, info_in_lib):
    self.min_temp = info_in_lib['temperature'][0]
    self.max_temp = info_in_lib['temperature'][1]
    self.offset = info_in_lib['temperature'][2]
  
  def _ensure_living_environment(self):
    env_temp = self.equipment_set.sensors_mgr.temperature
    if env_temp > self.max_temp + self.offset:
      if self.equipment_set.pump.start('temperature'):
        print("[EnvFactor] > Start watering by temperature: {}°C > {}+{}°C ({})".format(env_temp, self.max_temp, self.offset, Logger.time()))
    else:
      if self.equipment_set.pump.stop('temperature'):
        print("[EnvFactor] > Stop watering by temperature: {}°C <= {}+{}°C ({})".format(env_temp, self.max_temp, self.offset, Logger.time()))

class HumidityCondition(EnvironmentFactor):
  def __init__(self, info_in_lib):
    super().__init__('Humidity')

class LightCondition(EnvironmentFactor):
  def __init__(self, info_in_lib):
    super().__init__('Light')

class PPMCondition(EnvironmentFactor):
  def __init__(self, info_in_lib):
    super().__init__('ppm')

class pHCondition(EnvironmentFactor):
  def __init__(self, info_in_lib):
    super().__init__('pH')


ENV_MAP_TYPE = {
  "water": WaterCondition,
  "temperature": TemperatureCondition,
  "humidity": HumidityCondition,
  "light": LightCondition,
  "ppm": PPMCondition,
  "pH": pHCondition
}