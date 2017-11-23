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
  cmd('sudo systemctl enable {}'.format(service_name))
  cmd('sudo systemctl daemon-reload')
  cmd('sudo systemctl start {}'.format(service_name))
  # cmd('sudo systemctl status {}'.format(service_name))

def setup():
  # cmd('sudo apt-get install python3')
  cmd('git clone https://github.com/adafruit/Adafruit_Python_DHT.git')
  cmd('sudo python Adafruit_Python_DHT/setup.py install')

  cwd = os.getcwd()

  # Install main service
  cmd('chmod +x ./startup')
  install_service('insys', generate_service_file('insys', 'startup', cwd, 'INSYS FRESH VEGETABLES SERVICE'), )

  # Install update service
  cmd('chmod +x ./update')
  cmd('chmod +x ./update.py')
  install_service('insys_update', generate_service_file('insys_update', 'update', cwd, 'INSYS FRESH VEGETABLES UPDATE SERVICE'))


if __name__ == "__main__":
  setup()