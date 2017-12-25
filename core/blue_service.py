
from bluetooth import *
import threading

class BluetoothService:
  def __init__(self, handler):
    self.onRequest = handler
    self.clients = []
  
  def run(self):
    self.sock = BluetoothSocket(RFCOMM)
    self.sock.bind(("", PORT_ANY))
    self.sock.listen(1)
    self.port = self.sock.getsockname()[1]
    self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    advertise_service(self.sock, "SampleServer",\
                      service_id = self.uuid, service_classes = [ self.uuid, SERIAL_PORT_CLASS ],\
                      profiles = [ SERIAL_PORT_PROFILE ], \
#                     protocols = [ OBEX_UUID ] \
                      )
    print("Waiting for connection on RFCOMM channel %d" % self.port)

    try:
      while True:
        client = self.sock.accept()
        print("Accepted connection from ", client[1])
        # self.clients.append(client)
        t = threading.Thread(target=self.onRequest, args=(client))
        t.start()
        # self.clients.remove(client)
    except:
      self.sock.close()
  