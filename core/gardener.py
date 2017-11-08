# coding=utf-8

from datetime import datetime
from time import time,sleep
import datetime
import threading

class Gardener():
  def __init__(self, insysFirmware, plants=[], lazy=5):
    self.firmware = insysFirmware
    self.sensors = insysFirmware.sensors
    self.controllers = insysFirmware.controllers
    self.plants = plants
    self.lazy = lazy
    self.auto = True
    self.controllers.pins[0].eventDetect = self.onSetAutoState

  def onSetAutoState(self, pin):
    self.auto = pin.state

  def appendPlant(self, plant):
    self.plants.append(plant)

  def work(self):
    self.worker = threading.Thread(target=self._work)
    self.worker.start()
    print("[SYS] > Gardener start working")
    # self._work()

  def _work(self):
    while True:
      self.waterByTime()
      sleep(self.lazy)

  def waterByTime(self):
    now = datetime.datetime.now().time()
    for plant in self.plants:               # Duyệt qua tất cả cây trồng
      for stage in plant.growthStages:      # Duyệt qua tất cả giai đoạn phát triển
        for waterPoints in stage.schedule:  # Duyệt qua tất cả các thời điểm tưới nước/bón phân trong ngày
          waterPoints.waterIfInTime(self.controllers.pins[3])

