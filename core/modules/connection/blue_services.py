
from core.modules.connection.connection_mgr import *
from core.modules.connection.bluetoothctl import Bluetoothctl

try: from bluetooth import *
except: from dummy.bluetooth import *

import threading
import os
import struct

from subprocess import call
cmd = os.system

class BluetoothService:
  def __init__(self, on_request=None):
    self.on_request = on_request
    self.clients = []
    self.client_threads = []
    # self.blctl = Bluetoothctl()
  
  def _run(self):
    # self.blctl.make_discoverable()

    self.sock = BluetoothSocket(RFCOMM)
    self.sock.bind(("", PORT_ANY))
    self.sock.listen(1)
    self.port = self.sock.getsockname()[1]
    self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    #addr B8:27:EB:73:2A:5D
    try:
      advertise_service(self.sock, "SampleServer",\
                      service_id = self.uuid,\
                      service_classes = [ self.uuid, SERIAL_PORT_CLASS ],\
                      profiles = [ SERIAL_PORT_PROFILE ], \
#                     protocols = [ OBEX_UUID ] \
                      )
      print("[BLUETOOTH] >> Waiting for connection on RFCOMM channel %d" % self.port, flush=True)
    except:
      pass

    while True:
      try:
        client = self.sock.accept()
        if not client:
          print("[BLUETOOTH] > Client is null???", flush=True)
          break
        print("[BLUETOOTH] > Accepted connection from ", client[1], flush=True)
        self.clients.append(client)
        self.trust_client(client)
        t = threading.Thread(target=self.serve, kwargs=dict(client=client))
        t.start()
        self.client_threads.append(t)
      except Exception as err:
        print("[BLUETOOTH] > Something went wrong with client {}: {}".format(client[1], err), flush=True)
        # self.sock.close()

  def run(self):
    self.running_thread = threading.Thread(target=self._run)
    self.running_thread.start()
    
  def join(self):
    for client_thread in self.client_threads:
      try: client_thread.join()
      except: pass
    try: self.running_thread.join()
    except: pass

  def serve(self, client):
    client_sock = client[0]
    client_info = client[1]
    try:
      data = b''
      while True:
        # ready = select.select([client_sock], [], [], 15)
        # if ready[0]:
        #   data = client_sock.recv(1024)
        # else:
          # client_sock.close()
          # return
        data += client_sock.recv(2048)
        print("[BLUETOOTH] > recv: {}".format(data), flush=True)
        data = self.on_request(data, client_sock)
    except Exception as e:
      print("[BLUETOOTH] > Client disconnected ({}): {}".format(client_info, e), flush=True)
      client_sock.close()
      self.clients.remove(client)

  def trust_client(self, client):
    # self.blctl.pair(client[1][0])
    pass
  
  @staticmethod
  def setupBluetooth():
    cmd('sudo apt-get install bluetooth libbluetooth-dev')
    cmd('pip3 install pybluez')
    cmd('sudo systemctl start bluetooth && sleep 1')

    # Fix permission issue
    var_run_sdp_path = """[Unit]
Descrption=Monitor /var/run/sdp

[Install]
WantedBy=bluetooth.service

[Path]
PathExists=/var/run/sdp
Unit=var-run-sdp.service"""

    var_run_sdp_service = """[Unit]
Description=Set permission of /var/run/sdp

[Install]
RequiredBy=var-run-sdp.path

[Service]
Type=simple
ExecStart=/bin/chgrp bluetooth /var/run/sdp
ExecStartPost=/bin/chmod 662 /var/run/sdp"""

    cmd('sudo usermod -G bluetooth -a pi')
    cmd('sudo chgrp bluetooth /var/run/sdp')
    cmd('sudo echo "{}" > /etc/systemd/system/var-run-sdp.path'.format(var_run_sdp_path))
    cmd('sudo echo "{}" > /etc/systemd/system/var-run-sdp.service'.format(var_run_sdp_service))

    cmd('sudo systemctl daemon-reload')
    cmd('sudo systemctl enable var-run-sdp.path')
    cmd('sudo systemctl enable var-run-sdp.service')
    cmd('sudo systemctl start var-run-sdp.path')
    
# Lỗi khác
"""[advertise_service raise BluetoothError]

I'm guessing that you don't have the Serial Port Profile loaded? To do that, you'll need to
Code: Select all

sudo sdptool add SP
To do THAT, you need to run the Bluetooth daemon in 'compatibility' mode. Edit /etc/systemd/system/dbus-org.bluez.service and add '-C' after 'bluetoothd'. Reboot."""