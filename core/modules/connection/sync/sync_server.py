# coding=utf-8

from core.modules.connection.connection_mgr import ConnectionManager

class SyncServer:
  def __init__(self, conn_mgr):
    self.conn_mgr = conn_mgr