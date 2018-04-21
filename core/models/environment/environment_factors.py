# coding=utf-8

from core.modules.timepoint import TimePointGroup
from core.modules.logger import Logger
from core.modules.thread_looping import ThreadLooping

class EnvironmentFactor:
  def __init__(self, name, info_in_lib=None):
    self.name = name
    self.is_ensure_living_environment = False
    self.ensure_thread = ThreadLooping(target=self._ensure_living_environment, wait_time=2)
    # self.parse_from_lib(info_in_lib)

  def parse_from_lib(self, info_in_lib):
    pass

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
      self.ensure_thread.start()
    else:
      print("[EnvFactor] > equipment_set or user_plant is None")
  
  def stop_ensure_living_environment(self):
    self.ensure_thread.stop()

  def restart_ensure_living_environment(self):
    self.stop_ensure_living_environment()
    self.start_ensure_living_environment()

class WaterCondition(EnvironmentFactor):
  def __init__(self, info_in_lib):
    super().__init__('Water')
    self.parse_from_lib(info_in_lib)

  def parse_from_lib(self, info_in_lib):
    self.water_points = []
    for con in info_in_lib['water']:
      self.water_points.append(TimePointGroup(
        time_range = con['time_range'] if 'time_range' in con else None,
        time_info = con['time'] if 'time' in con else None,
        every = con['every'] if 'every' in con else None,
        duration = con['duration'] if 'duration' in con else '15'))

  def _ensure_living_environment(self):
    for wp in self.water_points:
      if wp.is_time_for_action(self.user_plant.planting_date_obj):
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
    if env_temp is not None:
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
    self.parse_from_lib(info_in_lib)

  def parse_from_lib(self, info_in_lib):
    self.light_points = []
    self.max_lux = self.min_lux = self.offset = None
    for con in info_in_lib['light']:
      if 'lux_range' in con:
        self.min_lux = con['lux_range'][0]
        self.max_lux = con['lux_range'][1]
        self.offset = con['lux_range'][2]
      elif 'time_range' in con or 'time' in con or 'every' in con:
        self.light_points.append(TimePointGroup(
          time_range = con['time_range'] if 'time_range' in con else None,
          time_info = con['time'] if 'time' in con else None,
          every = con['every'] if 'every' in con else None,
          duration = con['duration'] if 'duration' in con else '15'))
  
  def _ensure_living_environment(self):
    env_lux = self.equipment_set.sensors_mgr.light
    if env_lux is not None and self.max_lux is not None:
      if env_lux > self.max_lux + self.offset or env_lux < self.min_lux - self.offset:
        if self.equipment_set.light.start('light'):
          print("[EnvFactor] > Start lighting by light: {} lux out of [{}-{}]±{} lux ({})".format(env_lux, self.min_lux, self.max_lux, self.offset, Logger.time()))
      else:
        if self.equipment_set.light.stop('light'):
          print("[EnvFactor] > Stop lighting by light: {} lux in range [{}-{}]±{} lux ({})".format(env_lux, self.min_lux, self.max_lux, self.offset, Logger.time()))

    for lp in self.light_points:
      if lp.is_time_for_action(self.user_plant.planting_date_obj):
        if self.equipment_set.light.start('timing'):
          print("[EnvFactor] > Start lighting by time: {}".format(Logger.time()))
        break
    else:
      if self.equipment_set.light.stop('timing'):
        print("[EnvFactor] > Stop lighting by time: {}".format(Logger.time()))
        

class RotateCondition(EnvironmentFactor):
  def __init__(self, info_in_lib):
    super().__init__('Rotate')
    self.parse_from_lib(info_in_lib)

  def parse_from_lib(self, info_in_lib):
    self.rotate_points = []
    for con in info_in_lib['rotate']:
      self.rotate_points.append(TimePointGroup(
        time_range = con['time_range'] if 'time_range' in con else None,
        time_info = con['time'] if 'time' in con else None,
        every = con['every'] if 'every' in con else None,
        duration = con['duration'] if 'duration' in con else '15'))

  def _ensure_living_environment(self):
    for rp in self.rotate_points:
      if rp.is_time_for_action(self.user_plant.planting_date_obj):
        if self.equipment_set.rotate.start('timing'):
          print("[EnvFactor] > Start rotating by time: {}".format(Logger.time()))
        break
    else:
      if self.equipment_set.rotate.stop('timing'):
        print("[EnvFactor] > Stop rotating by time: {}".format(Logger.time()))

class PPMCondition(EnvironmentFactor):
  def __init__(self, info_in_lib):
    super().__init__('ppm')

class pHCondition(EnvironmentFactor):
  def __init__(self, info_in_lib):
    super().__init__('pH')


ENV_TYPE_MAPPING = {
  "water": WaterCondition,
  "temperature": TemperatureCondition,
  "humidity": HumidityCondition,
  "light": LightCondition,
  "rotate": RotateCondition,
  "ppm": PPMCondition,
  "pH": pHCondition
}