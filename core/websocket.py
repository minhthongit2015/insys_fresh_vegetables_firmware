import asyncio
import websockets
import socket

class WebSocketServer:
  def __init__(self, host="0.0.0.0", port=4444, request_handle=None, resolve_package=None):
    self.host = host
    self.port = port
    self.request_handle = request_handle
    self.resolve_package = resolve_package
  
  async def on_request(self, socket, path):
    print("[WEBSOCKET] > Connection from {}: {}".format(socket.remote_address, path))
    while True:
      data = await socket.recv()
      cmd, sub_cmd1, sub_cmd2, data, rest = self.resolve_package(bytes(list(map(ord,data))))
      if cmd: await socket.send(self.request_handle(data, cmd, sub_cmd1, sub_cmd2, None))
      if len(rest) <= 1: break
      else: data = rest
  
  @property
  def ipv4(self):
    try:
      ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
    except:
      ip = "localhost"
    return ip

  def run(self):
    print("[WEBSOCKET] > Websocket server is listening on {}:{}".format(self.ipv4, self.port))
    self.server = websockets.serve(self.on_request, self.host, self.port)
    asyncio.get_event_loop().run_until_complete(self.server)
    asyncio.get_event_loop().run_forever()