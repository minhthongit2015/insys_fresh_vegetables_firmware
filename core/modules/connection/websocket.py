import asyncio
import websockets
import socket

class WebSocketServer:
  def __init__(self, host="0.0.0.0", port=4444, on_request=None):
    self.host = host
    self.port = port
    self.on_request = on_request
  
  async def request_handle(self, socket, path):
    print("[WEBSOCKET] > Connection from {}: {}".format(socket.remote_address, path))
    data = ''
    while True:
      data += await socket.recv()
      data, package_2_send = self.on_request(bytes(list(map(ord,data))))
      if len(package_2_send) > 0:
        await socket.send(package_2_send)
  
  @property
  def ipv4(self):
    try:
      ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
    except:
      ip = "localhost"
    return ip

  def run(self):
    print("[WEBSOCKET] > Websocket server is listening on {}:{}".format(self.ipv4, self.port))
    self.server = websockets.serve(self.request_handle, self.host, self.port)
    asyncio.get_event_loop().run_until_complete(self.server)
    asyncio.get_event_loop().run_forever()