
try: from core.plant import Plant, GrowthStage, WaterPoints
except: from plant import Plant, GrowthStage, WaterPoints
import json

class PlantLibrary:
  def __init__(self, lib_file):
    try:
      f = open(lib_file, 'r', encoding='utf-8')
    except:
      print("[ERR] >> Failed to load plant library (check lirary file: {})".format(lib_file))
      return
    self.library = json.loads(f.read(), encoding="utf-8")
    print("[SYS] >> Plant library loaded.")
  
  def get_list(self):
    if not self.library: return
    plants = []
    for plant in self.library:
      plants.append(plant['name'])
    return plants
  
  def plant_parse(self, plant_in_lib):
    growth_stages = []
    for stage in plant_in_lib['growth_stages']:
      env = self.enviroment_translator(stage['enviroment'])
      growth_stages.append(GrowthStage(stage['stage_order'], stage['stage_name'], (stage['from'], stage['to']),
        env['water']))
    return Plant(plant_in_lib['name'], plant_in_lib['planting_date'], growth_stages)

  def enviroment_translator(self, enviroments):
    enviroments_parsed = {}
    for env in enviroments:
      if env['name'] == 'water':
        water_times = []
        for water in env['water']:
          if 'duration' not in water:
            water['duration'] = '15'  # default is water for 15 minutes
          if 'every' in water:
            water_times.append(WaterPoints(every=water['every'], duration=water['duration']))
          elif 'time' in water:
            water_times.append(WaterPoints(water['time'], water['duration']))
        enviroments_parsed['water'] = water_times
      else:
        enviroments_parsed[env['name']] = env[env['name']]
    return enviroments_parsed


if __name__ == "__main__":
  p = PlantLibrary('plants/vegetables.json')
  print(p.get_list())
  butterhead_lettuce = p.plant_parse(p.library[0])
