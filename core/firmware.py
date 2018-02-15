"""
"""
from core.models.equipment.equipment_mgr import EquipmentManager, CentralSet
from core.gardener import Gardener
from core.modules.connection.connection_mgr import ConnectionManager
from core.modules.connection.sync.mobile_sync import MobileSync

from core.modules.logger import Logger

class InSysFirmware:
  def __init__(self):
    self.equipment_mgr = EquipmentManager()

    self.central_equipment = self.equipment_mgr.central_equipments
    self.gardener = Gardener(self.equipment_mgr)

    self.conn_mgr = ConnectionManager()
    self.mobile_sync = MobileSync(self.conn_mgr, self.gardener)

    print("[Sys] >>> System initialized! ({})".format(Logger.datetime()))

  def run(self):
    try:
      # Start jobs
      self.gardener.start_working()

      self.conn_mgr.run()
      self.conn_mgr.startWebsocketServer()
    except:
      self.shutdown()

  def shutdown(self):
    print("[SYS] >>> System is shutting down...")
    self.gardener.stop_working()
    print("[SYS] >>> System shutdown!")
