
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
    self.clientThreads = []
  
  def run(self):
    self.discoverableThread = threading.Thread(target=self.discoverable)
    self.discoverableThread.start()

    self.sock = BluetoothSocket(RFCOMM)
    self.sock.bind(("", PORT_ANY))
    self.sock.listen(1)
    self.port = self.sock.getsockname()[1]
    self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    #addr B8:27:EB:73:2A:5D
    advertise_service(self.sock, "SampleServer",\
                      service_id = self.uuid,\
                      service_classes = [ self.uuid, SERIAL_PORT_CLASS ],\
                      profiles = [ SERIAL_PORT_PROFILE ], \
#                     protocols = [ OBEX_UUID ] \
                      )
    print("[BLUESRV] >> Waiting for connection on RFCOMM channel %d" % self.port)

    while True:
      try:
        client = self.sock.accept()
        print("[BLUESRV] > Accepted connection from ", client[1], flush=True)
        self.clients.append(client)
        self.trustClient(client)
        t = threading.Thread(target=self.onRequest, kwargs=dict(client=client, clients=self.clients))
        self.clientThreads.append(t)
        t.start()
      except:
        print("[BLUESRV] > Something went wrong with client: {}", client[1])
        # self.sock.close()
  
  def send(self, sock, data="", cmd=False):
    sock.send((chr(cmd) if cmd else "") + data + "\x00")
  
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
  
  @staticmethod
  def discoverable():
    cmd('sudo echo "power on\ndiscoverable on\npairable on\nagent NoInputNoOutput\n"; tee > /dev/null | bluetoothctl')

  def trustClient(self, client):
    cmd('sudo sudo echo "trust {}" | bluetoothctl'.format(client[1][0]))
    
  def join():
    try: self.discoverableThread.join()
    except: pass
    for client_thread in self.clientThreads:
      try: client_thread.join()
      except: pass

# Lỗi khác
"""[advertise_service raise BluetoothError]

I'm guessing that you don't have the Serial Port Profile loaded? To do that, you'll need to
Code: Select all

sudo sdptool add SP
To do THAT, you need to run the Bluetooth daemon in 'compatibility' mode. Edit /etc/systemd/system/dbus-org.bluez.service and add '-C' after 'bluetoothd'. Reboot."""