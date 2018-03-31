
from core.models.plant.user_plant import ListUserPlant
from core.models.equipment.equipment_set import EquipmentSet
from core.modules.config_mgr import ConfigManager

class Station:
  def __init__(self, info, plant_lib, serial_port=None, config_file_path=''):
    self.name = info['name']
    self.id = info['id']
    self.serial_port = serial_port
    if 'plants' in info:
      self.list_user_plant = ListUserPlant(info['plants'], plant_lib)
    else:
      self.list_user_plant = ListUserPlant([], plant_lib)

    self.equipment_set = EquipmentSet(owner_station=self, serial_port=self.serial_port)
    self.equipment_set.automation_led.addEventListener("on", self.start_ensure_living_environment)
    self.equipment_set.automation_led.addEventListener("off", self.stop_ensure_living_environment)
    self.equipment_set.sensors_mgr.add_state_change_listener(self.on_sensors_state_change)

    if config_file_path: self.station_cfg = ConfigManager(self.id, config_file_path)
    else: self.station_cfg = None
  
  def run(self):
    self.equipment_set.run()
    if self.equipment_set.sensors_mgr.state is not None:
      if self.equipment_set.hardware_check_led.turn(self.equipment_set.sensors_mgr.state, "workwell"):
        print("[Station:{}] > Sensors are working normally.".format(self.id), flush=True)
      else:
        print("[Station:{}] > Sensors are getting some problem.".format(self.id), flush=True)

    self.equipment_set.load_state(self.station_cfg)

  def attach_serial_port(self, serial_port):
    """ Gắn kết ``serial_port`` vào ``station``"""
    self.serial_port = serial_port
    self.equipment_set.attach_serial_port(serial_port)
  
  def update_station_sensors(self, sensor_data):
    self.equipment_set.sensors_mgr.update_sensors(sensor_data)
  
  def on_sensors_state_change(self, state):
    print("[Station:{}] > Check Sensors result: {}".format(self.id, state), flush=True)
    self.equipment_set.hardware_check_led.turn(state, "workwell")
  
  def start_ensure_living_environment(self, reason=''):
    print("[Station:{}] > Start ensure living environment.".format(self.id), flush=True)
    for user_plant in self.list_user_plant.plants:
      if user_plant.current_living_environment:
        for env in user_plant.current_living_environment:
          env.start_ensure_living_environment(self.equipment_set, user_plant)
  
  def stop_ensure_living_environment(self, reason=''):
    print("[Station:{}] > Stop ensure living environment.".format(self.id), flush=True)
    for user_plant in self.list_user_plant.plants:
      if user_plant.current_living_environment:
        for env in user_plant.current_living_environment:
          env.stop_ensure_living_environment()

  def set_state(self, equipment, state, reason):
    self.equipment_set.set_state(equipment, state, reason, self.station_cfg)

  def plant_new_plant(self, plant, plant_lib):
    self.list_user_plant.load([plant], plant_lib)
  
  def remove_plant(self, plant_id):
    self.list_user_plant.remove_plant(plant_id)

  def dump(self):
    station = {
      "name": self.name,
      "id": self.id,
      "equipment_set": self.equipment_set.dump(),
      "plants": self.list_user_plant.dump()
    }
    return station
