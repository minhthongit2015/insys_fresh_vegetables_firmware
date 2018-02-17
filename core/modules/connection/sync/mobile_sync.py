
from core.modules.connection.connection_mgr import ConnectionManager

import random
import json

class MobileSync:
  def __init__(self, conn_mgr, gardener):
    self._deviceId = ''
    self.deviceId = ''
    self.gardener = gardener
    self.conn_mgr = conn_mgr

    self.conn_mgr.register_request_handle(1, self.request_handle)
    self.conn_mgr.register_request_handle(2, self.request_handle)
    self.conn_mgr.register_request_handle(3, self.request_handle)
    self.conn_mgr.register_request_handle(4, self.request_handle)
  
  def request_handle(self, cmd, sub1, sub2, data, client):
    # if cmd is 1: # Connection/handshake + Authentication
    #   if self._deviceId == data.decode("utf-8"):
    #     self.token = random.randint(0, 255)
    #     return self.conn_mgr.send(client, self.deviceId)
    #     print("[BLUESRV] > bluetooth handshake: {} => {}".format(data[1:], self.token), flush=True)
    #   if sub1 is 1: # connect via Bluetooth
    #     # Recv Wifi UUID and Password
    #     # If have than connect to wifi and return [IP address]
    #     print("[BLUESRV] > handshake: return address {}:{}".format(self.conn_mgr.websocket_handle.ipv4, self.conn_mgr.websocket_handle.port))
    #     return self.conn_mgr.send(client, "{}:{}".format(self.conn_mgr.websocket_handle.ipv4, self.conn_mgr.websocket_handle.port), cmd, sub1, sub2)
    #     pass
    #   elif sub1 is 2: # connect via LAN return [1]
    #     pass
    #   elif sub1 is 2: # Authentication/Account Manager: recv username/password, check and return [Token]
    #     if sub2 is 1: # Register: [username, password]
    #       pass
    #     elif sub2 is 2: # Login: [username, password]
    #       pass
    #     elif sub2 is 3: # Delete
    #       pass
    #     elif sub2 is 4: # Change password: [pass_lenght:oldpass|pass_length:newpass]
    #       pass
    #     pass
    if cmd is 2: # cmd 2: get device state
      if sub1 is 1: # get info of all cylinder
        # None
        package = json.dumps(self.gardener.dump(), ensure_ascii=False)
        return self.conn_mgr.send(client, cmd, sub1, sub2, package)
      elif sub1 is 2: # get info of a specific cylinder
        # cylinder_name
        cylinder_name = json.loads(data)
        package = self.gardener.dump()
        return self.conn_mgr.send(client, package)
      # print("[BLUESRV] > transfer device state: {}".format(device_state), flush=True)
    elif cmd is 3: # cmd 3: Receive user command
      # [ cylinder_name, equipment_id, state ]
      cylinder_id, equipment, state = json.loads(data, encoding='utf-8')
      self.gardener.command_handle(cylinder_id, equipment, state)
      return self.conn_mgr.send(client, cmd, sub1, sub2, "YUP")
    # elif cmd is 4: # get sensors value
    #   if sub1 is 1: # get realtime sensors value
    #     hutemp = self.sensors['hutemp'].value
    #     pH = self.sensors['pH'].value
    #     device_state = "{}|{}|{}|{}".format(time(), hutemp[0], hutemp[1], pH)
    #     print("[BLUESRV] > realtime sensors value: {}".format(device_state), flush=True)
    #     return self.connection.send(client, device_state, cmd, sub1, sub2)
    #   elif sub1 is 2: # get records for last 6 hours
    #     records = self.logger.get_records_last_6h()
    #     sz_records = json.dumps(records)
    #     print("[BLUESRV] > records for last 6 hours ({} records).".format(len(records)), flush=True)
    #     print(sz_records, flush=True)
    #     return self.connection.send(client, sz_records.replace(' ',''), cmd, sub1, sub2)
    #   elif sub1 is 3: # get records since a exactly time
    #     pass
    # elif cmd is 5: # Manage Plant
    #   if sub1 is 1: # Get Plants List
    #     name,planting_date = data.split("|")
    #     new_plant = Plant()
    return ''