# coding=utf-8
from core.api import InSysServices, BaseAPI
from core.pins import Pin, ListPin, clean
from core.logger import Logger
from core.blue_service import BluetoothService

from core.sensors.hutemp_module_dht22 import DHT22
from core.sensors.phmeter_sen0161 import SEN0161

import http.client as httplib
import threading
import select
from time import sleep, time
import datetime
import random

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

    self.signalLights = ListPin(signalLights, default=[False])
    self.hardwareSignalLight = self.signalLights.pins[0]
    self.automodeSignalLight = self.signalLights.pins[1]
    self.controllers.pins[0].eventDetect.append(self.onAutoModeChange)
    self.enviromentSignalLight = self.signalLights.pins[2]
    self.networkSignalLight = self.signalLights.pins[3]

    self.logger = Logger('./log', 'humi_temp_pH')
    self.blueService = BluetoothService(self.onClientConnect)
    print("[SYS] >>> System Started Up!")
    print("[SYS] >>> Time: {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
    print("[SYS] >>> Firmware Version: {}".format(getFirmwareVersion()))

  def checkSystemState(self):
    if self.sensors['hutemp'].check() and self.sensors['pH'].check():
      self.hardwareSignalLight.on()
      print("[SYS] >> Hardware running normally.")
    else:
      print("[SYS] >> Some sensors had broken. Check device log for more detail.")

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
      "buttonId": pin.index,
      "active": pin.state
    }), headers = {"Content-type": "application/json"})
    self.request(switchAPI)
    print("[SYS] > Send sync to server pin {} to {}".format(pin.pin, pin.state))

  def putSensorData(self):
    while True:
      hutemp = self.sensors['hutemp'].value
      if hutemp == (0, 0): hutemp = self.sensors['hutemp'].default
      # if hutemp != self.sensors['hutemp'].default:
      #   break
      break
      
    pHValue = self.sensors['pH'].value
    print("pH: {}, hu: {}, temp: {}".format(pHValue, hutemp[0], hutemp[1]))
    
    self.logger.sensors_record(1, hutemp)

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
    if self.isError(test):
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

  def onClientConnect(self, client, clients):
    client_sock = client[0]
    client_info = client[1]
    try:
      data = b''
      while True:
        # ready = select.select([client_sock], [], [], 15)
        # if ready[0]:
        #   data = client_sock.recv(1024)
        # else:
          # client_sock.close()
          # return
        if len(data) <= 0:
          data = client_sock.recv(1024)
          print("[BLUESRV] > recv: {}".format(data))
        else:
          while data[0] == 3:
            data[1:]
          if len(data) <= 0: return
          print("[BLUESRV] > cont: {}".format(data))

        if len(data) <= 0: return
        if int(data[0]) == 0: # auth/handshake
          if self._deviceId == data[1:].decode("utf-8"):
            self.token = random.randint(0, 255)
            self.blueService.send(client_sock, str(self.token))
            print("[BLUESRV] > bluetooth handshake: {} => {}".format(data[1:], self.token), flush=True)
        elif int(data[0]) == 1: # command
          pinIndex = int(data[1])
          state = bool(data[2])
          print("[BLUESRV] > via bluetooth set pin {} to {}".format(self.controllers.pins[pinIndex].pin, state), flush=True)
          self.controllers.pins[pinIndex].turn(state)
          self.controllers.pins[pinIndex].emitter(self.controllers.pins[pinIndex])
          self.blueService.send(client_sock, "OK")
          data = data[3:]
        elif int(data[0]) == 2: # get device state
          hutemp = self.sensors['hutemp'].value_or_default
          pH = self.sensors['pH'].value_or_default
          device_state = "{}/{}|{}|{}".format(str(self.controllers), hutemp[0], hutemp[1], pH)
          print("[BLUESRV] > transfer device state: {}".format(device_state), flush=True)
          self.blueService.send(client_sock, device_state)
          data = data[1:]
        elif int(data[0]) == 3: # get sensors value
          hutemp = self.sensors['hutemp'].value_or_default
          pH = self.sensors['pH'].value_or_default
          device_state = "{}|{}|{}".format(hutemp[0], hutemp[1], pH)
          print("[BLUESRV] > transfer sensors value: {}".format(device_state), flush=True)
          self.blueService.send(client_sock, device_state)
          data = data[1:]
        # Close to avoid error
        # print("Close client {}".format(client_info))
        # client_sock.close()
        # clients.remove(client)

    except Exception as e:
      print("Close client {}".format(client_info))
      print("Reason: {}".format(e))
      client_sock.close()
      clients.remove(client)
      
    

  def run(self):
    print("[SYS] >> Start checking hardware (for now just sensors)")
    # self.checkSystemState()

    self.sensorThread = threading.Thread(target=self.putSensorDataLoop)
    self.sensorThread.start()
    print("[SYS] >> Start 'Sensor' thread")

    self.controlThread = threading.Thread(target=self.getSwitchStatesLoop)
    self.controlThread.start()
    print("[SYS] >> Start 'Control' thread")

    self.blueThread = threading.Thread(target=self.blueService.run)
    self.blueThread.start()
    print("[SYS] >> Start 'Bluetooth Control' thread")

  def join(self):
    try:
      self.sensorThread.join()
      self.controlThread.join()
    except:
      pass
    self.blueThread.join()

  def clean(self):
    clean()