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
    self.controllers.pins[0].eventDetect = self.onSetAutoState
    # self.controllers.pins[0].eventDetect = self.onSetAutoAdjust
    self.config_path = 'config.cfg'
    self.cfg = cfg.ConfigParser()
    self.cfg.read(self.config_path)
    if 'Gardener' not in self.cfg:
      self.cfg['Gardener'] = {}
      self.auto = True
    pin = self.pump = self.controllers[3]
    print("[SYS] > Auto mode is {}".format('on' if pin.state else 'off'))

    ###
    self.pump = self.controllers.pins[3]
    self.temperature = self.sensors['hutemp']
  
  def save(self):
    with open(self.config_path, 'w') as f: self.cfg.write(f)

  @property
  def auto(self):
    return self.cfg['Gardener']['auto']

  @auto.setter
  def auto(self, state):
    self.cfg['Gardener']['auto'] = str(bool(state))
    self.save()

  def onSetAutoState(self, pin):
    self.auto = pin.state
    print("[SYS] > Auto mode is {}".format('on' if pin.state else 'off'))

  def appendPlant(self, plant):
    self.plants.append(plant)

  def work(self):
    self.worker = threading.Thread(target=self._work)
    self.worker.start()
    print("[SYS] >> Gardener start working")
    # self._work()

  def _work(self):
    last = 0
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

  def water_by_time(self, stage, plant):
    if stage.is_water_time(plant):
      if self.pump.on():
        self.pump.emitter(self.pump)
      return True
    return False
  
  def water_by_temperature(self, stage):
    temperature = self.temperature.value[0]
    if not stage.temperature[0] - stage.temperature[2] < temperature < stage.temperature[1] + stage.temperature[2]:
      if self.pump.on():
        self.pump.emitter(self.pump)
      return True
    return False


