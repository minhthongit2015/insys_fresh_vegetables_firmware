# coding=utf-8

import core.modules.connection.blue_services as blue
import core.modules.connection.LAN_services as LAN
import core.modules.connection.websocket as websocket
from core.modules.connection.security import Security

import struct
from time import time, sleep
import json

class ConnectionManager:
  """#### Package structure
  
      Security   | DELM |           Header            | DELM | Data | END_SIGN 
  ---------------|------|-----|-----------|-----------|------|------|----------
   security_info | \xfe | cmd |   sub 1   |   sub 2   | \xfe | Data | \x00\x00 
         nb      |      | 1b  |    1b     |    1b     |      |  nb  |    2b    
  """
  header_length = 3
  _default_cmd = 255

  def __init__(self, host="0.0.0.0", port=4444):
    # self.LAN_handle = LAN.LANServices(host, port, request_handle)
    self.bluetooth_handle = blue.BluetoothService(self.on_request)
    self.websocket_handle = websocket.WebSocketServer(host, port, self.on_request)
    self._last_send = 0
    self.handle_mapping = { }
    self.security = Security()
    self.register_request_handle(1, self.hand_shake_handle)
  
  def attach_garden_info(self, garden_info):
    self.garden_info = garden_info
  
  @property
  def host(self):
    return self.websocket_handle.host

  def register_request_handle(self, cmd, handle=None):
    if handle is not None:
      self.handle_mapping[cmd] = handle

  def on_request(self, request, client=None):
    package_2_send = ''
    while True:
      (security_info, cmd, sub1, sub2, data, rest) = ConnectionManager.resolve_package(request)
      if security_info is None or cmd is None: # Dữ liệu nhận được không trọn vẹn
        if client is None: return (rest, 'Bad request')
        else: return rest

      if len(security_info) == self.security.token_length:
        if not self.security.check_token(security_info):
          package_2_send += self.send(client, cmd, sub1, sub2, 'Invalid Token')
        else:
          if cmd is 1 and sub1 is 1:
            self.security.tokens.pop(security_info) # refresh token
          package_2_send += self.dispath_request(cmd, sub1, sub2, data, client)
      else:
        if not self.security.check_security_code(security_info):
          package_2_send += self.send(client, cmd, sub1, sub2, 'Invalid Security Code')
        else:
          package_2_send += self.dispath_request(cmd, sub1, sub2, data, client)

      if len(rest) > 0: # Dữ liệu nhận được còn dư, tiếp tục xử lý (nhận hơn 1 gói tin)
        request = rest
      else:             # Dữ liệu nhận được vừa đủ 1 gói tin
        if client is None: return (rest, package_2_send)
        else: return rest
  
  def dispath_request(self, cmd, sub1=255, sub2=255, data=b'', client=None):
    if cmd in self.handle_mapping:
      if client is None:
        return self.handle_mapping[cmd](cmd, sub1, sub2, data, client)
      else:
        self.handle_mapping[cmd](cmd, sub1, sub2, data, client)
        return b''

  def run(self):
    # self.LAN_handle.run()
    self.bluetooth_handle.run()
    # self.websocket_handle.run()
  
  def startWebsocketServer(self):
    return self.websocket_handle.run()

  def join(self):
    # self.LAN_handle.join()
    self.bluetooth_handle.join()

  def send(self, client, cmd, sub1=255, sub2=255, data_2_send=''):
    header = ConnectionManager.build_header(cmd, sub1, sub2)
    package = "{}\xfe{}\x00\x00".format(header, data_2_send)
    delta = time() - self._last_send
    if delta < 1: sleep(1 - delta)
    self._last_send = time()
    if client: client.send(package)
    else: return package

  @staticmethod
  def build_header(cmd, sub1=255, sub2=255):
    cmd = chr(cmd)
    sub1 = chr(sub1)
    sub2 = chr(sub2)
    return "{}{}{}".format(cmd, sub1, sub2)


  @staticmethod
  def resolve_package(data):
    is_str = False
    if 'str' in str(type(data)):
      is_str = True

    default = [None, None, None, None, '' if is_str else b'', data]

    try:
      packages = data.split('\x00\x00' if is_str else b'\x00\x00')
      if len(packages) < 2:
        return default
    except:
      return default

    package = packages[0]
    rest = data[len(package)+2:]
    if len(data) < ConnectionManager.header_length:
      return default
    try:
      security_info, header, data = package.split('\xfe' if is_str else b'\xfe')
    except:
      return default
    cmd = ord(header[0]) if is_str else header[0]
    sub1 = ord(header[1]) if is_str else header[1]
    sub2 = ord(header[2]) if is_str else header[2]
    security_info = security_info if is_str else security_info.decode('utf-8')
    print("[CONNECTION] > package: {}".format((security_info, cmd, sub1, sub2, data, rest)))
    return (security_info, cmd, sub1, sub2, data, rest)

  def connectWifi(self, SSID, password):
    pass

  def hand_shake_handle(self, cmd, sub1, sub2, data, client):
    # cmd is 1
    if sub1 is 1: # [Get Access Token]
      if self.security.isEnable:
        token = self.security.generate_token()
        self.security.allow_token(token)
        package = token
      else:
        package = ''
    elif sub1 is 2: # [ Change Security Code ]
      old_securit_code, securit_code = json.loads(data)
      if self.security.check_security_code(old_securit_code):
        self.security.save_security_code(securit_code)
        package = 'OK'
      else:
        package = "Wrong_Security_Code"
    elif sub1 is 3: # [Config wifi]
      if sub2 is 1: # Stage 1: retrieve wifi list to let user choose
        package = json.dumps([
          {"SSID": "Minh Thai", "Pass": "nhatrang9x"},
          {"SSID": "IUHYRA", "Pass": "iuhyra@123"},
          {"SSID": "moidoiten", "Pass": "passla123"}
        ], ensure_ascii=False)
      elif sub2 is 2: # Stage 2: User choose one and send password of that wifi to us. Then we connect and resend the host.
        SSID, password = data.split(":")
        self.connectWifi(SSID, password)
        package = "{}".format(self.host)
    return self.send(client, cmd, sub1, sub2, package)