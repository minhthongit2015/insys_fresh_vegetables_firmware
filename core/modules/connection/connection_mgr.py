import core.modules.connection.blue_services as blue
import core.modules.connection.LAN_services as LAN
import core.modules.connection.websocket as websocket

import struct
from time import time, sleep

class ConnectionManager:
  """#### Package structure
  ________________________________________________________
  |             Header          | DELM | Data | END_SIGN |
  --------------------------------------------------------
  | cmd | sub cmd 1 | sub cmd 2 | \xfe | Data | \x00\x00 |
  | 1b  |    1b     |    1b     |      |  nb  |    2b    |
  """
  header_length = 3
  _default_cmd = 255

  def __init__(self, host="0.0.0.0", port=4444):
    # self.LAN_handle = LAN.LANServices(host, port, request_handle)
    self.bluetooth_handle = blue.BluetoothService(self.on_request)
    self.websocket_handle = websocket.WebSocketServer(host, port, self.on_request)
    self._last_send = 0
    self.handle_mapping = { }

  def register_request_handle(self, cmd, handle=None):
    if handle is not None:
      self.handle_mapping[cmd] = handle

  def on_request(self, request, client=None):
    package_2_send = ''
    while True:
      (cmd, sub1, sub2, data, rest) = ConnectionManager.resolve_package(request)
      if not cmd: # Dữ liệu nhận được không trọn vẹn
        if client is None: return (rest, package_2_send)
        else: return rest

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
    self.websocket_handle.run()

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
    cmd = chr(struct.unpack('B', struct.pack('b', cmd))[0])
    sub1 = chr(struct.unpack('B', struct.pack('b', sub1))[0])
    sub2 = chr(struct.unpack('B', struct.pack('b', sub2))[0])
    return "{}{}{}".format(cmd, sub1, sub2)


  @staticmethod
  def resolve_package(data):
    default = [None, None, None, b'', data]

    packages = data.split(b'\x00\x00')
    if len(packages) < 2:
      return default

    package = packages[0]
    rest = data[len(package)+2:]
    if len(data) < ConnectionManager.header_length:
      return default
    try:
      header, data = package.split(b'\xfe')
    except:
      return default
    cmd = struct.unpack('b', struct.pack('B', header[0]))[0]
    sub_cmd1 = struct.unpack('b', struct.pack('B', header[1]))[0]
    sub_cmd2 = struct.unpack('b', struct.pack('B', header[2]))[0]
    print("[CONNECTION] > package: {}".format((cmd, sub_cmd1, sub_cmd2, data, rest)))
    return (cmd, sub_cmd1, sub_cmd2, data, rest)