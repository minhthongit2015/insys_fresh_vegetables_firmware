
"""#### Package structure
 ______________________________________________________
|             Header          | DELM | Data | END_SIGN |
+:---------------------------:+:----:+:----:+:--------:+
| cmd | sub cmd 1 | sub cmd 2 | \x00 | Data | \x00\x00 |
| 1b  |    1b     |    1b     |      |  nb  |    2b    |
+-----+-----------+-----------+------+------+----------+
"""
import core.blue_services as blue
import core.LAN_services as LAN
import core.websocket as websocket
import struct

class Connection:
  header_length = 3

  def __init__(self, host="localhost", port=4444, request_handle=None):
    # self.LAN_handle = LAN.LANServices(host, port, request_handle)
    self.bluetooth_handle = blue.BluetoothService(request_handle, Connection.resolve_package)
    self.websocket_handle = websocket.WebSocketServer(host, port, request_handle, Connection.resolve_package)

  def run(self):
    # self.LAN_handle.run()
    self.bluetooth_handle.run()
    # self.websocket_handle.run()
  
  def startWebsocketServer(self):
    self.websocket_handle.run()

  def join(self):
    # self.LAN_handle.join()
    self.bluetooth_handle.join()

  def send(self, client, data, cmd=-1, sub1=-1, sub2=-1):
    cmd = chr(struct.unpack('B', struct.pack('b', cmd))[0])
    sub1 = chr(struct.unpack('B', struct.pack('b', sub1))[0])
    sub2 = chr(struct.unpack('B', struct.pack('b', sub2))[0])
    package = "{}{}{}\xfe{}\x00\x00".format(cmd, sub1, sub2, data)
    client.send(package)

  @staticmethod
  def resolve_package(data):
    package = data.split(b'\x00\x00')[0]
    rest = data[len(package)+2:]
    if len(data) < Connection.header_length: return [None, None, None, b'',b'']
    header, data = package.split(b'\xfe')
    cmd = struct.unpack('b', struct.pack('B', header[0]))[0]
    sub_cmd1 = struct.unpack('b', struct.pack('B', header[1]))[0]
    sub_cmd2 = struct.unpack('b', struct.pack('B', header[2]))[0]
    print("[CONNECTION] > package: {}".format((cmd, sub_cmd1, sub_cmd2, data, rest)))
    return (cmd, sub_cmd1, sub_cmd2, data, rest)