
from core.models.equipment.station import Station

import json
class StationManager:
  def __init__(self, plant_lib, station_file_path='./assets/stations.json', config_file_path='./configs/stations.cfg'):
    self.plant_lib = plant_lib  # Thư viện chăm sóc cây trồng
    self.stations = []  # Danh sách trạm
    self.stations_file_path = station_file_path # Đường dẫn tới file lưu thông tin trạm
    with open(station_file_path, 'r', encoding='utf-8') as fp:
      stations = json.load(fp)
      for station in stations:
        self.stations.append(Station(info=station, plant_lib=plant_lib, config_file_path=config_file_path))

  def run(self):
    for station in self.stations:
      station.run()

  def start_ensure_living_environment(self):
    for station in self.stations:
      station.start_ensure_living_environment()
  
  def stop_ensure_living_environment(self):
    for station in self.stations:
      station.stop_ensure_living_environment()
  
  def _generate_station_name(self):
    base_name = "Station"
    index = 0
    while True:
      for station in self.stations:
        if station.name == "{}-{:02d}".format(base_name, index):
          break
      else:
        return "{}-{:02d}".format(base_name, index)
      index += 1

  def attach_serial_port(self, serial_port):
    for station in self.stations:
      station.attach_serial_port(serial_port)

  def attach_station(self, station_id, serial_port):
    # Kiểm tra trụ đã có trong danh sách chưa
    # Nếu có thì gắn thêm serial_port vào equipment_set để có thể kết nối
    # Nếu chưa thì tạo mới với bộ equipment_set mới có kèm serial_port và lưu lại dữ liệu này xuống file
    station = self.get_station_by_id(station_id)
    if station is not None:
      station.equipment_set.attach_serial_port(serial_port)
    else:
      new_station = Station( info = {"id": station_id, "name": self._generate_station_name()},
                             plant_lib = self.plant_lib,
                             serial_port = serial_port)
      self.stations.append(new_station)
      self.save()

  def update_station_sensors(self, station_id, sensor_data):
    station = self.get_station_by_id(station_id)
    if station is not None:
      station.update_station_sensors(sensor_data)
  
  def get_station_by_name(self, name):
    for station in self.stations:
      if station.name == name:
        return station
    return None

  def get_station_by_id(self, station_id):
    for station in self.stations:
      if station.id == station_id:
        return station
    return None
  
  def set_state(self, cylinder_id, equipment, mode, reason):
    station = self.get_station_by_id(cylinder_id)
    station.set_state(equipment, mode, reason)

  def plant_new_plant(self, cylinder_id, plant_type, planting_date, alias):
    station = self.get_station_by_id(cylinder_id)
    station.plant_new_plant({"alias": alias,
                              "planting_date": planting_date,
                              "plant_type": plant_type,
                              "plant_id": self._generate_plant_id(plant_type)
                            }, self.plant_lib)
    self.save()

  def remove_plant(self, cylinder_id, plant_id):
    station = self.get_station_by_id(cylinder_id)
    station.remove_plant(plant_id)
    self.save()

  def _generate_plant_id(self, plant_type):
    signal = "{}-".format(plant_type)
    bigest_id = 0
    for station in self.stations:
      for plant in station.list_user_plant.plants:
        if signal in plant.plant_id:
          id = int(plant.plant_id.split('-')[1])
          if id > bigest_id:
            bigest_id = id
    return "{}-{}".format(plant_type, "000{}".format(bigest_id+1)[-3:])
  
  def dump(self):
    stations = []
    for station in self.stations:
      stations.append(station.dump())
    return stations

  def save(self):
    with open(self.stations_file_path, 'w', encoding='utf-8') as fp:
      stations = self.dump()
      for station in stations:
        station.pop('equipment_set')
      fp.write(json.dumps(stations, ensure_ascii=False, indent=2))

