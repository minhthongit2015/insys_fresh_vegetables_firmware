
from core.models.equipment.sensors.sensors_mgr import SensorsManager
from core.models.equipment.actions import SignalAction, WaterAction, NutrientAction, LightAction

class EquipmentSet:
  def __init__(self, owner_station, serial_port=None, emulate_sensors=False):
    self.owner_station = owner_station
    self.sensors_mgr = SensorsManager(serial_port=serial_port, owner_station=owner_station, emulate_sensors=emulate_sensors)
    self.hardware_check_led = SignalAction(serial_port=serial_port, signal_name='Hardware', owner_station=owner_station)
    self.envs_check_led = SignalAction(serial_port=serial_port, signal_name='Envs', owner_station=owner_station)
    self.automation_led = SignalAction(serial_port=serial_port, signal_name='AutoMode', owner_station=owner_station)
    self.pump = WaterAction(serial_port=serial_port, owner_station=owner_station)
    self.nutrient = NutrientAction(serial_port=serial_port, owner_station=owner_station)
    self.light = LightAction(serial_port=serial_port, owner_station=owner_station)

    self.equip_mapping = {
      "hardware": self.hardware_check_led,
      "environment": self.envs_check_led,
      "automation": self.automation_led,
      "pump": self.pump,
      "nutrient": self.nutrient,
      "light": self.light
    }
  
  def run(self):
    self.sensors_mgr.run()
  
  def attach_serial_port(self, serial_port):
    self.sensors_mgr.attach_serial_port(serial_port)
    self.hardware_check_led.attach_serial_port(serial_port)
    self.envs_check_led.attach_serial_port(serial_port)
    self.automation_led.attach_serial_port(serial_port)
    self.pump.attach_serial_port(serial_port)
    self.nutrient.attach_serial_port(serial_port)
    self.light.attach_serial_port(serial_port)

  def load_state(self, cfg):
    """ Nạp dữ liệu từ file config lên (cfg lưu đối tượng ConfigManager) """
    cfg.read()
    for equip in self.equip_mapping:
      equip_cfg = cfg.getc(equip)
      if equip_cfg is not None:
        self.equip_mapping[equip].turn(equip_cfg[0], equip_cfg[1])
  
  def set_state(self, equipment, state, reason, cfg):
    equip = self.equip_mapping[equipment]
    
    # Nếu là do người dùng đặt thì ưu tiên lên trên và gỡ bỏ các lý do khác
    if reason == "UserSet": equip.clear_reasons()
    
    # Điều khiển thiết bị theo yêu cầu
    rs = equip.turn(state, reason)
    cfg.set(equipment, [state, equip.reasons]) # Lưu trạng thái thiết bị

    # Khi bật chế độ tự động => Tắt tất cả các thiết bị và chuyển quyển về hệ thống
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
      "pump": self.pump.state,
      "nutrient": self.nutrient.state,
      "light": self.light.state,
      "sensors": self.sensors_mgr.dump(),
      "hardware": self.hardware_check_led.state,
      "environment": self.envs_check_led.state,
      "automation": self.automation_led.state
    }
    return equipment_set