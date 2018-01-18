"""
Quản lý kết nối thông qua LAN
"""
import socket
import socketserver
import threading
import struct
from core.connection import *

class LANHandler(socketserver.BaseRequestHandler):
  # def request_handle(self, data, cmd, sub_cmd):
    # pass

  def handle(self):
    try:
      data = b''
      while True:
        if len(data) <= 0:
          data = self.request.recv(1024).strip()
          print("[LAN] > recv: {}".format(data))
        header, cmd, sub_cmd1, sub_cmd2, data = Connection.resolve_frame(data)
        if not header: continue
        self.request_handle(data, cmd, sub_cmd1, sub_cmd2, self)
    except Exception as e:
      print("[LAN] > Client disconnected ({}): {}".format(self.client_address, e))
      self.finish()

  def send(self, data):
    self.request.sendall(data)
  
class LANServices:
  def __init__(self, host="localhost", port=4444, request_handle=None):
    self.host = host
    self.port = port
    LANHandler.request_handle = request_handle

  def run(self):
    print("[LAN] > LAN Server is listening on {}:{}".format(socket.gethostbyname(socket.gethostname()), self.port))
    self.server = socketserver.TCPServer((self.host, self.port), LANHandler)
    self.server.serve_forever()
    pass