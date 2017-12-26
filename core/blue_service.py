
try: from bluetooth import *
except: from dummy.bluetooth import *
import threading
import os

from subprocess import call
cmd = os.system

class BluetoothService:
  def __init__(self, handler):
    self.onRequest = handler
    self.clients = []
  
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
    print("[BLUESRV] >> Waiting for connection on RFCOMM channel %d" % self.port)

    try:
      while True:
        client = self.sock.accept()
        print("[BLUESRV] > Accepted connection from ", client[1])
        # self.clients.append(client)
        threading.Thread(target=self.onRequest, args=(client)).start()
        # self.clients.remove(client)
    except:
      self.sock.close()
  
  @staticmethod
  def setupBluetooth():
    cmd('sudo apt-get install bluetooth libbluetooth-dev')
    cmd('pip3 install pybluez')
    cmd('sudo systemctl start bluetooth && sleep 1')
    cmd('echo "power on\ndiscoverable on\npairable on\nagent NoInputNoOutput\ndefault-agent\n" | bluetoothctl')