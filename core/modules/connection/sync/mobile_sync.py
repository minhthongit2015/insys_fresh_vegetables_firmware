
from core.modules.connection.connection_mgr import ConnectionManager

import random
import json

class MobileSync:
  def __init__(self, conn_mgr, gardener):
    self.gardener = gardener
    self.conn_mgr = conn_mgr

    self.conn_mgr.register_request_handle(1, self.request_handle)
    self.conn_mgr.register_request_handle(2, self.request_handle)
    self.conn_mgr.register_request_handle(3, self.request_handle)
    self.conn_mgr.register_request_handle(4, self.request_handle)

    self.password = "1234"
  
  def request_handle(self, cmd, sub1, sub2, data, client):
    if cmd is 1: # [Connection/handshake + Authentication]
      # if self._deviceId == data.decode("utf-8"):
      #   self.token = random.randint(0, 255)
      #   return self.conn_mgr.send(client, self.deviceId)
      #   print("[BLUESRV] > bluetooth handshake: {} => {}".format(data[1:], self.token), flush=True)
      if sub1 is 1: # Check device signature
        package = json.dumps({"Identify": "Garden", "password":False}, ensure_ascii=False)
      elif sub1 is 2: # Authentication
        if data == self.password:
          package = "OK"
        else:
          package = "WrongSecurityCode"
      elif sub1 is 3: # Config wifi
        if sub2 is 1: # Stage 1: retrieve wifi list to let user choose
          package = json.dumps([
            {"SSID": "Minh Thai", "Pass": "nhatrang9x"},
            {"SSID": "IUHYRA", "Pass": "iuhyra@123"},
            {"SSID": "moidoiten", "Pass": "passla123"}
          ], ensure_ascii=False)
        elif sub2 is 2: # Stage 2: User choose one and send password of that wifi to us. Then we connect and resend the host.
          SSID, password = data.split(":")
          self.conn_mgr.connectWifi(SSID, password)
          package = "{}".format(self.conn_mgr.host)
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
    elif cmd is 2: # cmd 2: [Get Garden State]
      if sub1 is 1: # get info of all cylinder
        package = json.dumps(self.gardener.dump(), ensure_ascii=False)
      elif sub1 is 2: # get info of a specific cylinder
        cylinder_id = data
        if sub2 is 1: # get cylinder state (equipments, sensors) (used to realtime update)
          package = json.dumps(self.gardener.get_cylinder_info(cylinder_id), ensure_ascii=False)
        elif sub2 is 2: # get cylinder records for last 6 hours (used to draw chart)
          package = json.dumps(self.gardener.get_records_from(cylinder_id, 6))
    elif cmd is 3: # cmd 3: [Set Garden State]
      # [ cylinder_name, equipment_id, state ]
      cylinder_id, equipment, state = json.loads(data, encoding='utf-8')
      self.gardener.command_handle(cylinder_id, equipment, state)
      package = "YUP"
    elif cmd is 4: # Manage Plant
      if sub1 is 1: # Create new plant
        cylinder_id, plant_type, planting_date, alias = json.loads(data)
        self.gardener.plant_new_plant(cylinder_id, plant_type, planting_date, alias)
        package = json.dumps(self.gardener.dump(), ensure_ascii=False)
        # new_plant = Plant(info)
      elif sub1 is 2: # Remove Plant
        cylinder_id, plant_id = json.loads(data)
        self.gardener.remove_plant(cylinder_id, plant_id)
        package = json.dumps(self.gardener.dump(), ensure_ascii=False)
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
    return self.conn_mgr.send(client, cmd, sub1, sub2, package)
    