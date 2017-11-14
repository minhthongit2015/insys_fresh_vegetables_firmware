# coding=utf-8

from datetime import datetime
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
    self.config_path = 'config.cfg'
    self.cfg = cfg.ConfigParser()
    self.cfg.read(self.config_path)
    if 'Gardener' not in self.cfg:
      self.cfg['Gardener'] = {}
      self.auto = True
  
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
    # self.worker = threading.Thread(target=self._work)
    # self.worker.start()
    print("[SYS] >> Gardener start working")
    self._work()

  def _work(self):
    while True:
      if self.auto: self.waterByTime()
      sleep(self.lazy)

  def waterByTime(self):
    now = datetime.datetime.now().time()
    for plant in self.plants:               # Duyệt qua tất cả cây trồng
      for stage in plant.growth_stages:     # Duyệt qua tất cả giai đoạn phát triển
        if stage.water_if_in_stage(plant, self.controllers.pins[3]):
          pass

