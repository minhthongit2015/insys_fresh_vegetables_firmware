# coding=utf-8

from time import time,sleep
import datetime
import threading
try: import configparser as cfg
except: import ConfigParser as cfg

class Gardener():
  def __init__(self, insysFirmware, plants=[], lazy=5, nutritive_lazy=30, nutritive_timestep=3):
    self.firmware = insysFirmware
    self.sensors = insysFirmware.sensors
    self.controllers = insysFirmware.controllers
    self.plants = plants
    self.lazy = lazy
    self.pump = self.controllers.pins[3]
    self.nutritive_lazy = nutritive_lazy
    self.nutritive_valve = self.controllers.pins[1]
    self.nutritive_timestep = nutritive_timestep
    self.autopin = self.controllers.pins[0]
    
    self.config_path = 'config.cfg'
    self.cfg = cfg.ConfigParser()
    self.cfg.read(self.config_path)
    if 'Gardener' not in self.cfg:
      self.cfg['Gardener'] = {}
      self.auto = True

    self.autopin.turn(self.auto)
    self.controllers.pins[0].eventDetect = self.onSetAutoState

    self.temperature = self.sensors['hutemp']
    self.pH = self.sensors['pH']
    print("[GARDENER] > Auto mode is {}".format('on' if self.autopin.state else 'off'))
  
  def save(self):
    with open(self.config_path, 'w') as f: self.cfg.write(f)

  @property
  def auto(self):
    return self.cfg.getboolean('Gardener', 'auto')

  @auto.setter
  def auto(self, state):
    self.autopin.turn(state)
    print("[GARDENER] > Auto mode is {}".format('on' if state else 'off'))
    self.cfg['Gardener']['auto'] = str(bool(state)) # option value must be string!
    self.save()

  def onSetAutoState(self, pin):
    self.auto = pin.state

  def appendPlant(self, plant):
    self.plants.append(plant)

  def work(self):
    self.worker1 = threading.Thread(target=self._water)
    self.worker1.start()
    self.worker2 = threading.Thread(target=self._manure)
    self.worker2.start()
    print("[GARDENER] >> Gardener start working")
    # self._manure()

  def join(self):
    self.worker1.join()
    self.worker2.join()

  def _water(self):
    last = time()
    while True:
      if self.auto: self.water()
      delta = time() - last
      if delta < self.lazy:
        sleep(self.lazy - delta)
      last = time()

  def water(self):
    for plant in self.plants:                       # Duyệt qua tất cả cây trồng
      cur_stage = plant.get_current_growth_stage()
      if self.water_by_temperature(cur_stage):
        return True
      if self.water_by_time(cur_stage, plant):
        return True
    if self.pump.off():
      self.pump.emitter(self.pump)
      print("[GARDENER] > stop watering {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))

  def water_by_time(self, stage, plant):
    if stage.is_water_time(plant):
      if self.pump.on():
        self.pump.emitter(self.pump)
        print("[GARDENER] > start watering by time {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
      return True
    return False
  
  def water_by_temperature(self, stage):
    temperature = self.temperature.value[1]
    if temperature > stage.temperature[1] + stage.temperature[2]:
      if self.pump.on():
        self.pump.emitter(self.pump)
        print("[GARDENER] > start watering by temp {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
      return True
    return False

  def _manure(self):
    last = time()
    self.adjusting_nutritive = False
    while True:
      if self.auto: self.manure()
      delta = time() - last
      if delta < self.nutritive_lazy:
        sleep(self.nutritive_lazy - delta)
      last = time()

  def manure(self):
    for plant in self.plants:                       # Duyệt qua tất cả cây trồng
      cur_stage = plant.get_current_growth_stage()
      if self.manure_by_pH(cur_stage):
        return True
    if self.nutritive_valve.off():
      self.nutritive_valve.emitter(self.nutritive_valve)
      print("[GARDENER] > close nutritive valve {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
      self.adjusting_nutritive = False

  def manure_by_pH(self, stage):
    if self.pH.value < stage.pH[0] or self.pH.value > stage.pH[1]:
      if self.nutritive_valve.on():
        sleep(self.nutritive_timestep)
        self.nutritive_valve.off()
        if not self.adjusting_nutritive:
          self.nutritive_valve.emitter(self.nutritive_valve)
          print("[GARDENER] > open nutritive valve {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
          self.adjusting_nutritive = True
      return True
    return False




