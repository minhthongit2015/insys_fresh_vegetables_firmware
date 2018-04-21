# coding=utf-8

"""
Quản lý kết nối thông qua LAN
"""
from core.modules.connection.connection_mgr import *
import socket
import socketserver
import threading
import struct

class LANHandler(socketserver.BaseRequestHandler):
  # def request_handle(self, data, cmd, sub_cmd):
    # pass

  def handle(self):
    print("[LAN] > Client connect: {}".format(self.request))
    try:
      data = b''
      while True:
        if len(data) <= 0:
          data = self.request.recv(1024).strip()
          print("[LAN] > recv: {}".format(data))
        header, cmd, sub_cmd1, sub_cmd2, data = ConnectionManager.resolve_package(data)
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

  # def get_ip_address(self, ifname):
  #   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  #   return socket.inet_ntoa(fcntl.ioctl(
  #       s.fileno(),
  #       0x8915,  # SIOCGIFADDR
  #       struct.pack('256s', ifname[:15])
  #   )[20:24])

  @property
  def ipv4(self):
    try:
      ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
    except:
      ip = "localhost"
    return ip

  def run(self):
    print("[LAN] > LAN Server is listening on {}:{}".format(self.ipv4, self.port))
    # self.server = socketserver.TCPServer((self.host, self.port), LANHandler)
    # self.server.serve_forever()

    # asyncio.get_event_loop().run_until_complete(websockets.serve(self.hello, self.host, self.port))
    # asyncio.get_event_loop().run_forever()

  def join(self):
    pass