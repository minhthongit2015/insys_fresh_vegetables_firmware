#!/usr/bin/python

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
  cmd('sudo apt-get install build-essential python-dev')

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
      cmd('sudo apt-get install bluetooth libbluetooth-dev')
      cmd('pip3 install pybluez')
      """
      I'm guessing that you don't have the Serial Port Profile loaded? To do that, you'll need to
Code: Select all

sudo sdptool add SP
To do THAT, you need to run the Bluetooth daemon in 'compatibility' mode. Edit /etc/systemd/system/dbus-org.bluez.service and add '-C' after 'bluetoothd'. Reboot."""
      """
      Permission denies

      sudo usermod -G bluetooth -a pi
      sudo chgrp bluetooth /var/run/sdp
      """

  cwd = os.getcwd()

  # Install main service
  cmd('chmod +x ./startup')
  install_service('insys', generate_service_file('insys', 'startup', cwd, 'INSYS FRESH VEGETABLES - CORE SERVICE'), )

  # Install update service
  cmd('chmod +x ./update')
  cmd('chmod +x ./update.py')
  install_service('insys_update', generate_service_file('insys_update', 'update', cwd, 'INSYS FRESH VEGETABLES - UPDATE SERVICE'))

  # Install Camera streaming service
  cmd('chmod +x ./core/camera')
  install_service('insys_camera', generate_service_file('insys_camera', 'core/camera', cwd, 'INSYS FRESH VEGETABLES - CAMERA TRACKING SERVICE'))


if __name__ == "__main__":
  setup()