
from bluetooth import *
import threading

from subprocess import call
def cmd(command):
  call(command.split(' '))

class BluetoothService:
  def __init__(self, handler):
    self.onRequest = handler
    self.clients = []

  def setupBluetooth(self):
    cmd('echo -e "power on\ndiscoverable on\npairable on\nagent NoInputNoOutput\ndefault-agent\n" | bluetoothctl')
  
  def run(self):
    threading.Thread(target=self.setupBluetooth).start()

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
        threading.Thread(target=self.onRequest, args=(client)).start()
        # self.clients.remove(client)
    except:
      self.sock.close()
  