# coding=utf-8
from core.api import InSysServices, BaseAPI
from core.pins import Pin, ListPin
from core.hutemp_module_dht22 import DHT22
import threading
from time import sleep, time
import datetime

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
  def __init__(self, deviceId, switchPins=[], sensorPin=-1, refreshTimeControl=4, refreshTimeSensor=10):
    InSysServices.__init__(self, 'insysdemo.azurewebsites.net')
    self._deviceId = deviceId
    self.controllers = ListPin(switchPins, reverse=[True], default=[False], emitter=[self.sync_switch_state])
    # self.controllers.setEventDetect([self.sync_switch_state])
    self.sensors = DHT22(sensorPin)
    self.refreshTimeControl = refreshTimeControl
    self.refreshTimeSensor = refreshTimeSensor
    print("[SYS] > System Started Up!")
    print("[SYS] > Time: {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
    print("[SYS] > Firmware Version: {}".format(getFirmwareVersion()))

  def getSwitchStates(self):
    getStatusAPI = BaseAPI('post', '/api/device/getstatus', {}, self.paramsToJSON({'deviceId': self._deviceId}),
      headers = {"Content-type": "application/json"})
    self.request(getStatusAPI, self.resolveDeviceStatus)

  def resolveDeviceStatus(self, response, api):
    result = response.read()
    status = self.parseResult(result)
    if len(status['data']) > 0:
      pinStates = status['data'][0]['frame'].split('#')
      for (pin, state) in zip(self.controllers.pins, pinStates):
        pin.turn(state)

  def getSwitchStatesLoop(self):
    while True:
      self.getSwitchStates()
      sleep(self.refreshTimeControl)

  def sync_switch_state(self, pin):
    switchAPI = BaseAPI('put', '/api/device/Buttons/Active', {}, self.paramsToJSON({
      "localdeviceId": self._deviceId,
      "buttonId": 4,
      "active": pin.state
    }), headers = {"Content-type": "application/json"})
    self.request(switchAPI)
    print("> Send sync to server pin {} to {}".format(pin.pin, pin.state))

  def putSensorData(self):
    sensorData = self.sensors.read()
    putSensorDataAPI = BaseAPI('put', '/api/device/updates', {}, self.paramsToJSON({
      "gateWayId": "59336609883fa03a18cd48d7",
      "token": "c3RyaW5nOjJBd29uWEc5UEwwZXRLN01zejcvdWc9PQ==",
      "devices": [{
        "deviceId": self._deviceId,
        "humidity": sensorData[0],
        "temperature": sensorData[1],
      }]
    }), headers = {"Content-type": "application/json"})
    self.request(putSensorDataAPI, callback=lambda x,y: 1)
  
  def putSensorDataLoop(self):
    while True:
      self.putSensorData()
      if self.refreshTimeSensor-2 > 0:
        sleep(self.refreshTimeSensor-2)

  def run(self):
    syncThread = threading.Thread(target=self.getSwitchStatesLoop)
    sensorThread = threading.Thread(target=self.putSensorDataLoop)

    print("[SYS] > Start 'Control' thread")
    syncThread.start()
    
    print("[SYS] > Start 'Sensor' thread")
    sensorThread.start()