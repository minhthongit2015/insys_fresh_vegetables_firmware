# coding=utf-8

from time import time,sleep
import datetime
import threading
try: import configparser as cfg
except: import ConfigParser as cfg

from collections import namedtuple
PinStruct = namedtuple('PinStruct', 'pin state index')

class Gardener():
  def __init__(self, insysFirmware, plants=[], water_freq_time=5, nutritive_lazy=30, nutritive_timestep=3):
    self.firmware = insysFirmware
    self.sensors = insysFirmware.sensors
    self.controllers = insysFirmware.controllers
    self.signalLights = insysFirmware.signalLights
    self.plants = plants

    self.autopin = self.controllers.pins[0]
    self.water_freq_time = water_freq_time

    self.pump = self.controllers.pins[3]
    self.nutritive_valve = self.controllers.pins[1]
    self.nutritive_timestep = nutritive_timestep
    self.nutritive_lazy = nutritive_lazy
    
    self.is_watering_by_time = False
    self.is_watering_by_temp = False
    
    self.config_path = 'config.cfg'
    self.cfg = cfg.ConfigParser()
    self.cfg.read(self.config_path)
    if 'Gardener' not in self.cfg:
      self.cfg['Gardener'] = {}
      self.auto = True

    self.autopin.turn(self.auto)
    self.controllers.pins[0].eventDetect.append(self.onSetAutoState)

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
    print("[GARDENER] > Auto mode is {}".format('on' if pin.state else 'off'))
    self.cfg['Gardener']['auto'] = str(bool(pin.state)) # option value must be string!
    self.save()

  def appendPlant(self, plant):
    self.plants.append(plant)

  def work(self):
    self.water_by_time_thread = threading.Thread(target=self.water_by_time)
    self.water_by_time_thread.start()
    self.water_by_temp_thread = threading.Thread(target=self.water_by_temperature)
    self.water_by_temp_thread.start()
    self.manure_by_pH_thread = threading.Thread(target=self._manure)
    self.manure_by_pH_thread.start()
    print("[GARDENER] >> Gardener start working")

  def join(self):
    try: self.water_by_time_thread.join()
    except: pass
    try: self.water_by_temp_thread.join()
    except: pass
    try: self.manure_by_pH_thread.join()
    except: pass

  def water_by_time(self):
    last = 0
    while True:
      delta = time() - last
      if delta < self.water_freq_time: sleep(self.water_freq_time - delta)
      last = time()
      if self.auto and not self.is_watering_by_temp:
        water = False
        for plant in self.plants:
          cur_stage = plant.get_current_growth_stage()
          if cur_stage.is_water_time(plant):
            water = True
            self.is_watering_by_time = True
            if self.pump.on():
              print("[GARDENER] > start watering by time: ({})".format(datetime.datetime.now().strftime('%H:%M:%S')))
              self.pump.emitter(self.pump)
        if not water and self.pump.off():
          self.is_watering_by_time = False
          print("[GARDENER] > stop watering by time {}".format(datetime.datetime.now().strftime('%H:%M:%S')))
          self.pump.emitter(self.pump)
      elif self.is_watering_by_time:          # Swap water decision channel to water by temp
        self.is_watering_by_time = False
        print("[GARDENER] > Swap from water by time to water by temp.")

  def water_by_temperature(self):
    last = 0
    while True:
      delta = time() - last
      if delta < self.water_freq_time: sleep(self.water_freq_time - delta)
      last = time()
      if self.auto:
        water = False
        for plant in self.plants:
          cur_stage = plant.get_current_growth_stage()
          min_temp = cur_stage.temperature[0]
          max_temp = cur_stage.temperature[1]
          deviation = cur_stage.temperature[2]
          env_temp = self.temperature.value[1]
          if env_temp > max_temp + deviation:
            water = True
            self.is_watering_by_temp = True
            if self.pump.on():
              print("[GARDENER] > start watering by temp: {}°C [{}, {}]±{}  ({})".format(env_temp, min_temp, max_temp, deviation, datetime.datetime.now().strftime('%H:%M:%S')))
              self.pump.emitter(self.pump)
              self.signalLights.pins[2].on()
        if self.is_watering_by_temp and not water and self.pump.off():
          self.is_watering_by_temp = False
          self.signalLights.pins[2].off()
          print("[GARDENER] > stop watering by temp: {}°C [{}, {}]±{}  ({})".format(env_temp, min_temp, max_temp, deviation, datetime.datetime.now().strftime('%H:%M:%S')))
          self.pump.emitter(self.pump)

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
          self.nutritive_valve.emitter(PinStruct(pin=self.nutritive_valve.pin, state=True, index=self.nutritive_valve.index))
          print("[GARDENER] > open nutritive valve {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
          self.adjusting_nutritive = True
      return True
    return False




