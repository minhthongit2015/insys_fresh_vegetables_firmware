# coding=utf-8
from core.api import InSysServices, BaseAPI
from core.pins import Pin, ListPin, clean
from core.hutemp_module_dht22 import DHT22
from core.pHmeter.phmeter_sen0161 import SEN0161
from core.logger import Logger
import http.client as httplib
from core.blue_service import BluetoothService
import random

import threading
import select
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
  def __init__(self, deviceId, switchPins=[], sensors=[4, 0x04], refreshTimeControl=4, refreshTimeSensor=10):
    InSysServices.__init__(self, 'insysdemo.azurewebsites.net')
    self._deviceId = deviceId
    self.controllers = ListPin(switchPins, reverse=[True], default=[False], emitter=[self.sync_switch_state])
    self.sensors = {"hutemp": DHT22(sensors[0]), "pH": SEN0161(sensors[1])}
    self.refreshTimeControl = refreshTimeControl
    self.refreshTimeSensor = refreshTimeSensor
    self.logger = Logger('./log', 'humi_temp_pH')
    self.blue = BluetoothService(self.onClientConnect)
    print("[SYS] >>> System Started Up!")
    print("[SYS] >>> Time: {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
    print("[SYS] >>> Firmware Version: {}".format(getFirmwareVersion()))

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
      print("[SYS] > Failed to resolve device status result. Detail as below:")
      if "Error 403 - This web app is stopped" in str(result):
        print(' + [DEEP_DEBUGGING] > Error 403 - This web app is stopped')
      print(e)
      print('-------------- {} --------------'.format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))

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
      "buttonId": 4,
      "active": pin.state
    }), headers = {"Content-type": "application/json"})
    self.request(switchAPI)
    print("> Send sync to server pin {} to {}".format(pin.pin, pin.state))

  def putSensorData(self):
    while True:
      hutemp = self.sensors['hutemp'].value
      if hutemp == (0, 0): hutemp = self.sensors['hutemp'].default
      # if hutemp != self.sensors['hutemp'].default:
      #   break
      break
      
    pHValue = self.sensors['pH'].value
    print("pH: {}, hu: {}, temp: {}".format(pHValue, hutemp[0], hutemp[1]))

    putSensorDataAPI = BaseAPI('put', '/api/device/updates', {}, self.paramsToJSON({
      "gateWayId": "59336609883fa03a18cd48d7",
      "token": "c3RyaW5nOjJBd29uWEc5UEwwZXRLN01zejcvdWc9PQ==",
      "devices": [{
        "deviceId": self._deviceId,
        "humidity": hutemp[0],
        "temperature": hutemp[1],
        "pH": pHValue
      }]
    }), headers = {"Content-type": "application/json"})
    record = "{} {} {}".format(hutemp[0], hutemp[1], pHValue)
    test = self.request(putSensorDataAPI, callback=lambda res,api: self.checkSensorPutResponse(record,res,api))
    if not isinstance(test, httplib.HTTPSConnection):
      self.checkSensorPutResponse(record)
  
  def putSensorDataLoop(self):
    last = time()
    while True:
      self.putSensorData()
      delta = time() - last
      if delta < self.refreshTimeSensor:
        sleep(self.refreshTimeSensor - delta)
      last = time()

  def checkSensorPutResponse(self, record, response=None, api=None):
    if (response != None and response.code != 200) or response == None:
      self.logger.record(record)

  def onClientConnect(self, client_sock, client_info):
    print(self, client_sock, client_info)
    try:
      while True:
        data = b''
        ready = select.select([client_sock], [], [], 15)
        if ready[0]:
          data = client_sock.recv(1024)
        # else:
          # client_sock.close()
          # return
        
        print(data)
        if len(data) <= 0: return
        if int(data[0]) == 0: # auth/handshake
          if self._deviceId == data[1:].decode("utf-8"):
            self.token = random.randint(0, 255)
            client_sock.send(str(self.token))
            print("___ bluetooth handshake: {} => {}".format(data[1:], self.token))
        elif int(data[0]) == 1: # command
          pin = int(data[1])
          state = bool(data[2])
          print("___ bluetooth set pin {} to {}".format(self.controllers.pins[pin].pin, state))
          self.controllers.pins[pin].turn(state)
          self.controllers.pins[pin].emitter(self.controllers.pins[pin])
          client_sock.send(str(1))
        elif int(data[0]) == 2: # get device state
          print("___ bluetooth send sync state: {}".format(str(self.controllers.pins)))
          client_sock.send(str(self.controllers.pins))
    except:
      client_sock.close()
    

  def run(self):
    self.sensorThread = threading.Thread(target=self.putSensorDataLoop)
    # self.sensorThread.start()
    # self.putSensorDataLoop()
    print("[SYS] >> Start 'Sensor' thread")

    self.controlThread = threading.Thread(target=self.getSwitchStatesLoop)
    # self.controlThread.start()
    # self.getSwitchStatesLoop()
    print("[SYS] >> Start 'Control' thread")

    self.blueThread = threading.Thread(target=self.blue.run)
    self.blueThread.start()
    print("[SYS] >> Start 'Bluetooth Control' thread")

  def join(self):
    self.sensorThread.join()
    self.controlThread.join()

  def clean(self):
    clean()