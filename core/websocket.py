import asyncio
import websockets

class WebSocketServer:
  def __init__(self, host="localhost", port=4444, request_handle=None):
    self.host = host
    self.port = port
    self.request_handle = request_handle
  
  async def on_request(self):
    pass
  
  def run(self):
    asyncio.get_event_loop().run_until_complete(websockets.serve(self.on_request, self.host, self.port))
    asyncio.get_event_loop().run_forever()