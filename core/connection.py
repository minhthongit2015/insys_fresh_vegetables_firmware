
"""#### Frame structure
 ______________________________________________________
|             Header          | DELM | Data | END_SIGN |
+:---------------------------:+:----:+:----:+:--------:+
| cmd | sub cmd 1 | sub cmd 2 | \x00 | Data | \x00\x00 |
| 1b  |    1b     |    1b     |      |  nb  |    2b    |
+-----+-----------+-----------+------+------+----------+
"""
import core.blue_services as blue
import core.LAN_services as LAN
import core.connection
import struct

class Connection:
  header_length = 7

  def __init__(self, host="localhost", port=4444, request_handle=None):
    self.LAN_handle = LAN.LANServices(host, port, request_handle)
    self.bluetooth_handle = blue.BluetoothService(request_handle)

  def run(self):
    self.LAN_handle.run()
    self.bluetooth_handle.run()

  def join(self):
    self.LAN_handle.join()
    self.bluetooth_handle.join()

  def send(self, client, data, cmd=-1, sub1=-1, sub2=-1):
    frame = str(cmd) + str(sub1) + str(sub2) + struct.pack("i", len(data) + Connection.header_length) + data
    client.send(frame)

  @staticmethod
  def resolve_frame(data):
    package = data.split(b'\x00\x00')[0]
    rest = data[len(package)+2:]
    if len(data) < Connection.header_length: return [None]*5
    header, data = package.split(b'\x00')
    cmd = header[0]
    sub_cmd1 = header[1]
    sub_cmd2 = header[2]
    return (cmd, sub_cmd1, sub_cmd2, data, rest)