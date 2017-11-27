# coding=utf-8

from time import time,sleep
import datetime
import threading
try: import configparser as cfg
except: import ConfigParser as cfg

class Gardener():
  def __init__(self, insysFirmware, plants=[], lazy=5):
    self.firmware = insysFirmware
    self.sensors = insysFirmware.sensors
    self.controllers = insysFirmware.controllers
    self.plants = plants
    self.lazy = lazy
    self.pump = self.controllers.pins[3]
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
    print("[GARDENER] > Auto mode is {}".format('on' if pin.state else 'off'))

  def appendPlant(self, plant):
    self.plants.append(plant)

  def work(self):
    self.worker = threading.Thread(target=self._work)
    self.worker.start()
    print("[GARDENER] >> Gardener start working")
    # self._work()

  def _work(self):
    last = time()
    while True:
      if self.auto: self.water()
      delta = time() - last
      if delta < self.lazy:
        sleep(self.lazy - delta)
      last = time()

  def water(self):
    now = datetime.datetime.now().time()
    for plant in self.plants:               # Duyệt qua tất cả cây trồng
      for stage in plant.growth_stages:     # Duyệt qua tất cả giai đoạn phát triển
        if stage.is_in_stage(plant):
          if self.water_by_temperature(stage):
            return True
          if self.water_by_time(stage, plant):
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


