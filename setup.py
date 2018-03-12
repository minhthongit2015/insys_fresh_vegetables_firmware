#!/usr/bin/python3

from subprocess import call
import os

def generate_service_file(service_name, exec_path, working_directory, description):
  return """# /etc/systemd/system

[Unit]
Description={}
After=network.target multi-user.target

[Service]
Type=idle
ExecStart={}/{}
WorkingDirectory={}
Restart=always
User=pi

[Install]
WantedBy=network.target multi-user.target
Alias={}.service
""".format(description, working_directory, exec_path, working_directory, service_name)

def cmd(command):
  call(command.split(' '))

cmd = os.system

def install_service(service_name, service_file):
  service_name = service_name.replace(' ', '')
  print('[SETUP] > Install {} service'.format(service_name))
  insys_service_file = open('{}.service'.format(service_name), 'w')
  insys_service_file.write(service_file)
  insys_service_file.close()
  cmd('sudo mv {}.service /etc/systemd/system'.format(service_name))
  cmd('chmod +x /etc/systemd/system/{}.service'.format(service_name))
  cmd('sudo systemctl enable {}.service'.format(service_name))
  cmd('sudo systemctl daemon-reload')
  cmd('sudo systemctl start {}.service'.format(service_name))
  # cmd('sudo systemctl status {}'.format(service_name))

def setup():
  # cmd('sudo apt-get install python3')
  # cmd('sudo apt-get update')
  # cmd('sudo apt-get install build-essential python-dev')

  while True:
    try:
      import Adafruit_DHT
      break
    except:
      cmd('git clone https://github.com/adafruit/Adafruit_Python_DHT.git')
      cmd('cd Adafruit_Python_DHT')
      cmd('sudo python3 setup.py install')
      cmd('cd ..')

  while True:
    try:
      import bluetooth
      break
    except:
      from core.blue_service import BluetoothService
      BluetoothService.setupBluetooth()

  while True:
    try:
      import websockets
      break
    except:
      cmd('sudo pip3 install websockets')

  # Camera setup
  # cmd('sudo apt-get install libmp3lame-dev -y; sudo apt-get install autoconf -y; sudo apt-get install libtool -y; sudo apt-get install checkinstall -y; sudo apt-get install libssl-dev -y')
  # cmd('mkdir /home/pi/src && cd /home/pi/src && git clone git://git.videolan.org/x264 && cd x264 && ./configure --host=arm-unknown-linux-gnueabi --enable-static --disable-opencl && sudo make && sudo make install')
  # cmd('cd && cd /home/pi/src && sudo git clone git://source.ffmpeg.org/ffmpeg.git && cd ffmpeg && sudo ./configure --enable-gpl --enable-nonfree --enable-libx264 --enable-libmp3lame && sudo make -j$(nproc) && sudo make install')
  # cmd('sudo apt-get install -y libx264-dev')
  # cmd('sudo apt-get install -y ffmpeg')

  cwd = os.getcwd()

  # Install main service
  cmd('chmod +x ./startup')
  install_service('insys', generate_service_file('insys', 'startup', cwd, 'INSYS SMART GARDEN - CORE SERVICE'), )

  # Install update service
  cmd('chmod +x ./update')
  cmd('chmod +x ./update.py')
  install_service('insys_update', generate_service_file('insys_update', 'update', cwd, 'INSYS SMART GARDEN - UPDATE SERVICE'))

  # Install Camera streaming service
  cmd('chmod +x ./camera')
  install_service('insys_camera', generate_service_file('insys_camera', 'camera', cwd, 'INSYS SMART GARDEN - CAMERA TRACKING SERVICE'))

  # Base
  cmd('chmod +x ./uninstall.py')

if __name__ == "__main__":
  setup()