# coding=utf-8

"""
"""
from core.gardener import Gardener
from core.modules.connection.connection_mgr import ConnectionManager
from core.modules.connection.sync.mobile_sync import MobileSync
from core.modules.connection.sync.station_sync import StationSync

from core.modules.logger import Logger

class InSysFirmware:
  def __init__(self):
    print("\r\n---------------------------------------------------")

    # self.central_equipment = self.equipment_mgr.central_equipments
    self.gardener = Gardener()

    self.conn_mgr = ConnectionManager()
    self.mobile_sync = MobileSync(self.conn_mgr, self.gardener)
    self.station_sync = StationSync(self.gardener)

    self.gardener.attach_serial_port(self.station_sync)

    print("[System] >>> System initialized! ({})".format(Logger.datetime()))
    print("---------------------------------------------------")

  def run(self):
    try:
      # Start jobs
      self.station_sync.start()
      self.gardener.start_working()

      self.conn_mgr.run()
      self.conn_mgr.startWebsocketServer()
    except:
      self.shutdown()

  def shutdown(self):
    print("[System] >>> System is shutting down...")
    self.gardener.stop_working()
    print("[System] >>> System shutdown!")
