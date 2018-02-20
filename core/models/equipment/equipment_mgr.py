
from core.modules.config_mgr import ConfigManager
from core.models.gpio.gpio import Pin
from core.models.environment.sensors.sensors_mgr import SensorsManager
from core.models.equipment.actions import *


class EquipmentManager:
  def __init__(self, emulate_sensors=False):
    self.emulate_sensors = emulate_sensors

    self.cfg = ConfigManager('EquipmentConfig')
    self.central_equipments = CentralSet(self.cfg.getz('Central'))

    list_equipment_sets = self.cfg.getz('EquipmentSets')
    self.equipment_sets = []
    for equipment_set in list_equipment_sets:
      self.equipment_sets.append(EquipmentSet(equipment_set['name'], equipment_set['config'][0], equipment_set['config'][1:], emulate_sensors))

  def get_by_name(self, name):
    for equipment_set in self.equipment_sets:
      if equipment_set.name == name:
        return equipment_set

class EquipmentSet:
  def __init__(self, name, i2c_addr=0, pins=[], emulate_sensors=False):
    self.name = name
    self.sensors_mgr = SensorsManager(i2c_addr, pins[0], emulate_sensors)
    self.hardware_check_led = SignalAction(pins[1], 'Hardware')
    self.envs_check_led = SignalAction(pins[2], 'Envs')
    self.automation_led = SignalAction(pins[3], 'AutoMode')
    self.pump = WaterAction(pins[4])
    self.nutrient = NutrientAction(pins[5])
    self.light = LightAction(pins[6])

    self.equip_mapping = {
      "hardware": self.hardware_check_led,
      "environment": self.envs_check_led,
      "automation": self.automation_led,
      "pump": self.pump,
      "nutrient": self.nutrient,
      "light": self.light
    }

  def load_state(self, cfg):
    """ Nạp dữ liệu từ file config lên (cfg lưu đối tượng ConfigManager) """
    cfg.read()
    for equip in self.equip_mapping:
      equip_cfg = cfg.getc(equip)
      if equip_cfg is not None:
        self.equip_mapping[equip].turn(equip_cfg[0], equip_cfg[1])
  
  def set_state(self, equipment, state, reason, cfg):

    equip = self.equip_mapping[equipment]
    if reason == "UserSet": equip.clear_reasons() # If reason is User Set then remove all others
    rs = equip.turn(state, reason)
    cfg.set(equipment, [state, equip.reasons])
  
    if equipment == "automation" and state is True:
      self.pump.turn(False, 'UserSet')
      self.nutrient.turn(False, 'UserSet')
      self.light.turn(False, 'UserSet')
      cfg.set("pump", [self.pump.state, self.pump.reasons])
      cfg.set("nutrient", [self.pump.state, self.nutrient.reasons])
      cfg.set("light", [self.pump.state, self.light.reasons])

    return rs

  def dump(self):
    equipment_set = {
      "name": self.name,
      "pump": self.pump.state,
      "nutrient": self.nutrient.state,
      "light": self.light.state,
      "sensors": self.sensors_mgr.dump(),
      "hardware": self.hardware_check_led.state,
      "environment": self.envs_check_led.state,
      "automation": self.automation_led.state
    }
    return equipment_set

class CentralSet:
  """
  ### Chức năng của các đèn hiệu
  - **automation_led**: Đèn báo chế độ tự động đang bật hay tắt trên tất cả các trụ.
    + ``Đỏ``: Tất cả trụ đều ở chế độ thủ công.
    + ``Vàng``: Một số trụ thủ công, một số trụ tự động.
    + ``Xanh``: Tất cả trụ đều ở chế độ tự động.
  - **hardware_check_led**: Đèn báo tình trạng hoạt động của các cảm biến trên tất cả các trụ.
    + ``Đỏ``: Tất cả cảm biến trên tất cả các trụ đều không hoạt động.
    + ``Vàng``: Một số cảm biến ở các trụ không hoạt động.
    + ``Xanh``: Tất cả cảm biến đều hoạt động bình thường.
  - **envs_check_led**: Đèn báo tình trạng môi trường sinh trưởng trên tất cả các trụ.
    + ``Đỏ``: Tất cả các trụ đều đang gặp điều kiện môi trường không thuận lợi.
    + ``Vàng``: Một số trụ đang gặp điều kiện môi trường không thuận lợi.
    + ``Xanh``: Tất cả các trụ đều đang ở điều kiện môi trường thuận lợi.
  """
  def __init__(self, pins):
    self.hardware_check_led = Pin(pins[0])
    self.envs_check_led = Pin(pins[1])
    self.automation_led = Pin(pins[2])