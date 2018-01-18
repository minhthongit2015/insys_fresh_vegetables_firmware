# coding=utf-8
from core.api import InSysServices, BaseAPI
from core.pins import Pin, ListPin, clean
from core.logger import Logger
from core.connection import Connection

from core.sensors.hutemp_module_dht22 import DHT22
from core.sensors.phmeter_sen0161 import SEN0161

import http.client as httplib
import threading
import select
from time import sleep, time
import datetime
import random
import json

def getLocalDeviceId(fname):
  with open(fname) as f: return f.readline()[:24]

def getFirmwareVersion():
  try:
    with open('version.ini', 'r+') as f:
      ver = f.read()
      return ver if ver != '' else '0.0.0.0'
  except:
    return '0.0.0.0'
    pass

class InsysFirmware(InSysServices):
  def __init__(self, deviceId, switchPins=[], sensors=[4, 0x04], signalLights=[],\
    refreshTimeControl=4, refreshTimeSensor=10):
    InSysServices.__init__(self, 'insysdemo.azurewebsites.net')
    self._deviceId = deviceId
    self.controllers = ListPin(switchPins, reverse=[True], default=[False], emitter=[self.sync_switch_state])
    self.sensors = {"hutemp": DHT22(sensors[0]), "pH": SEN0161(sensors[1])}
    self.refreshTimeControl = refreshTimeControl
    self.refreshTimeSensor = refreshTimeSensor

    # Setup signal lights to determine whenever sensors are working normally or broken down
    self.signalLights = ListPin(signalLights, default=[False])
    self.hardwareSignalLight = self.signalLights.pins[0]
    self.automodeSignalLight = self.signalLights.pins[1]
    self.controllers.pins[0].eventDetect.append(self.onAutoModeChange)
    self.enviromentSignalLight = self.signalLights.pins[2]
    self.networkSignalLight = self.signalLights.pins[3]

    # Adding event listener to determine whenever sensors are working normally or broken down
    self.sensors['hutemp'].on_broken = self.on_hutemp_broken
    self.sensors['pH'].on_broken = self.on_pH_broken
    self.sensors['hutemp'].on_working = self.on_hutemp_working
    self.sensors['pH'].on_working = self.on_pH_working

    self.logger = Logger('./log', 'humi_temp_pH')
    self.envs_log = self.logger.create_log_type("envs", "./log")
    self.connection = Connection(request_handle=self.onClientConnect)
    print("[SYS] >>> System Started Up!")
    print("[SYS] >>> Time: {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
    print("[SYS] >>> Firmware Version: {}".format(getFirmwareVersion()))

  def on_hutemp_working(self):
    if self.sensors['pH'].is_normally:
      self.hardwareSignalLight.on()
      print("[SYS] > [Hardware Checking]: All sensors are working normally.")
  def on_pH_working(self):
    if self.sensors['hutemp'].is_normally:
      self.hardwareSignalLight.on()
      print("[SYS] > [Hardware Checking]: All sensors are working normally.")
  def on_hutemp_broken(self):
    print("[SYS] > [Hardware Checking]: hutemp sensor is not working normally.")
    self.hardwareSignalLight.off()
  def on_pH_broken(self):
    print("[SYS] > [Hardware Checking]: pH sensor is not working normally.")
    self.hardwareSignalLight.off()

  def onAutoModeChange(self, pin):
    self.automodeSignalLight.turn(pin.state)

  def onNetworkError(self, err):
    self.networkSignalLight.off()
    print("[SYS] >> Network error at: {}\r\n{}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), str(err)))

  def onNetworkOnline(self):
    self.networkSignalLight.on()
    print("[SYS] >> Network is online at: {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))

  def getSwitchStates(self):
    getStatusAPI = BaseAPI('post', '/api/device/getstatus', {}, self.paramsToJSON({'deviceId': self._deviceId}),
      headers = {"Content-type": "application/json"})
    self.request(getStatusAPI, self.resolveDeviceStatus)

  def resolveDeviceStatus(self, response, api):
    result = response.read()
    try:
      status = self.parseResult(result)
      if len(status['data']) > 0:
        pinStates = status['data'][0]['frame'].split('#')
        if bool(int(pinStates[0])): # if auto mode is on, then skip overwrite pin state
          return
        for (pin, state) in zip(self.controllers.pins, pinStates):
          # print("Pin {} to {}".format(pin, state))
          pin.turn(state)
    except Exception as e:
      err = '403 - Web app is stopped' if "Error 403 - This web app is stopped" in str(result) else e
      print("[SYS] > Failed to sync with server: {} ({})".format(err, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))

  def getSwitchStatesLoop(self):
    last = time()
    while True:
      self.getSwitchStates()
      delta = time() - last
      if delta < self.refreshTimeControl:
        sleep(self.refreshTimeControl - delta)
      last = time()

  def sync_switch_state(self, pin):
    switchAPI = BaseAPI('put', '/api/device/Buttons/Active', {}, self.paramsToJSON({
      "localdeviceId": self._deviceId,
      "buttonId": pin.index,
      "active": pin.state
    }), headers = {"Content-type": "application/json"})
    self.request(switchAPI)
    print("[SYS] > Send sync to server pin {} to {}".format(pin.pin, pin.state))

  def putSensorData(self):
    hutemp = self.sensors['hutemp'].value
    pH = self.sensors['pH'].value
    self.logger.dump_record(self.envs_log, '{} {} {}'.format(pH, hutemp[1], hutemp[0]))
    print("[DUMP] > pH: {}, hu: {}, temp: {}".format(pH, hutemp[0], hutemp[1]), flush=True)

    putSensorDataAPI = BaseAPI('put', '/api/device/updates', {}, self.paramsToJSON({
      "gateWayId": "59336609883fa03a18cd48d7",
      "token": "c3RyaW5nOjJBd29uWEc5UEwwZXRLN01zejcvdWc9PQ==",
      "devices": [{
        "deviceId": self._deviceId,
        "humidity": hutemp[0],
        "temperature": hutemp[1],
        "pH": pH
      }]
    }), headers = {"Content-type": "application/json"})
    self.request(putSensorDataAPI)
  
  def putSensorDataLoop(self):
    last = 0
    while True:
      delta = time() - last
      if delta < self.refreshTimeSensor:
        sleep(self.refreshTimeSensor - delta)
      last = time()
      self.putSensorData()

  def onClientConnect(self, data, cmd, sub1, sub2, client):
      if cmd is 1: # Connection/handshake + Authentication
        if self._deviceId == data.decode("utf-8"):
          self.token = random.randint(0, 255)
          self.connection.send(client, self.deviceId)
          print("[BLUESRV] > bluetooth handshake: {} => {}".format(req[1:], self.token), flush=True)
        if sub1 is 1: # connect via Bluetooth
          # Recv Wifi UUID and Password
          # If have than connect to wifi and return [IP address]
          pass
        elif sub1 is 2: # connect via LAN return [1]
          pass
        elif sub1 is 2: # Authentication/Account Manager: recv username/password, check and return [Token]
          if sub2 is 1: # Register: [username, password]
            pass
          elif sub2 is 2: # Login: [username, password]
            pass
          elif sub2 is 3: # Delete
            pass
          elif sub2 is 4: # Change password: [pass_lenght:oldpass|pass_length:newpass]
            pass
          pass
      elif cmd is 2: # Control device
        pinIndex = int(data[1])
        state = bool(data[2])
        print("[BLUESRV] > via bluetooth set pin {} to {}".format(self.controllers.pins[pinIndex].pin, state), flush=True)
        self.controllers.pins[pinIndex].turn(state)
        self.controllers.pins[pinIndex].emitter(self.controllers.pins[pinIndex])
        self.connection.send(client, "OK")
      elif cmd is 3: # get device state
        hutemp = self.sensors['hutemp'].value
        pH = self.sensors['pH'].value
        device_state = "{}/{}|{}|{}".format(str(self.controllers), hutemp[0], hutemp[1], pH)
        print("[BLUESRV] > transfer device state: {}".format(device_state), flush=True)
        self.connection.send(client, device_state)
      elif cmd is 4: # get sensors value
        if sub1 is 1: # get realtime sensors value
          print("[BLUESRV] > transfer realtime sensors value: {}".format(device_state), flush=True)
          hutemp = self.sensors['hutemp'].value
          pH = self.sensors['pH'].value
          device_state = "{}|{}|{}|{}".format(time(), hutemp[0], hutemp[1], pH)
          self.connection.send(client, device_state)
        elif sub1 is 1: # get records for last 6 hours
          print("[BLUESRV] > transfer records for last 6 hours ({} records).".format(len(records)))
          records = self.logger.get_records_last_6h()
          sz_records = json.dumps(records)
          self.connection.send(client, sz_records)
        elif sub1 is 2: # get records since a exactly time
          pass
      elif cmd is 5: # Create and modify Plant
        if sub1 is 1:
          name,planting_date = data.split("|")
          new_plant = Plant()
      
    

  def run(self):
    print("[SYS] >> Starts checking hardware (just sensors)")
    self.sensors['hutemp'].run()
    self.sensors['pH'].run()

    print("[SYS] >> Start 'Sensor' thread")
    self.sensorThread = threading.Thread(target=self.putSensorDataLoop)
    self.sensorThread.start()

    print("[SYS] >> Start 'Control' thread")
    # self.controlThread = threading.Thread(target=self.getSwitchStatesLoop)
    # self.controlThread.start()

    print("[SYS] >> Start 'Bluetooth Control' thread")
    self.connection_thread = threading.Thread(target=self.connection.run)
    self.connection_thread.start()

  def join(self):
    try:
      self.sensorThread.join()
      self.controlThread.join()
    except:
      pass
    self.blueThread.join()
    self.blueService.join()

  def clean(self):
    clean()