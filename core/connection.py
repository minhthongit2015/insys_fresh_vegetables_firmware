
"""#### Frame structure
 ___________________________________________________
|             Header                         | Data |
+:---------------------------:+:------------:+:----:+
| cmd | sub cmd 1 | sub cmd 2 | Frame length | Data |
| 1b  |    1b     |    1b     |      4b      |  nb  |
+-----+-----------+-----------+--------------+------+
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

  def send(self, client, data, cmd=-1, sub1=-1, sub2=-1):
    frame = str(cmd) + str(sub1) + str(sub2) + struct.pack("i", len(data) + Connection.header_length) + data
    client.send(frame)

  @staticmethod
  def resolve_frame(data):
    if len(data) < Connection.header_length: return [None]*5
    header = data[:Connection.header_length]
    cmd = header[0]
    sub_cmd1 = header[1]
    sub_cmd2 = header[2]
    package_length = struct.unpack('d', header[3:])
    data = data[len(header) : package_length]
    return (header, cmd, sub_cmd1, sub_cmd2, data)