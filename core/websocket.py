import asyncio
import websockets
import socket

class WebSocketServer:
  def __init__(self, host="localhost", port=4444, request_handle=None, resolve_package=None):
    self.host = host
    self.port = port
    self.request_handle = request_handle
    self.resolve_package = resolve_package
  
  async def on_request(self, websocket, path):
    print("[WEBSOCKET] > Connection from {}: {}".format(websockets, path))
    pass
  
  @property
  def ipv4(self):
    try:
      ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
    except:
      ip = "localhost"
    return ip

  def run(self):
    print("[WEBSOCKET] > Websocket server is listening on {}:{}".format(self.ipv4, self.port))
    asyncio.get_event_loop().run_until_complete(websockets.serve(self.on_request, self.host, self.port))
    asyncio.get_event_loop().run_forever()