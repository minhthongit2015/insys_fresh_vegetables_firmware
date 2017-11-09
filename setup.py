#!/usr/bin/python

from subprocess import call
import os

def generate_service_file(service_name, exec_path, working_directory):
  return """# /etc/systemd/system

[Unit]
Description=INSYS FRESH VEGETABLES UPDATE SERVICE
After=multi-user.target

[Service]
Type=idle
ExecStart={}/{}
WorkingDirectory={}
Restart=always

[Install]
WantedBy=multi-user.target
Alias={}.service
""".format(working_directory, exec_path, working_directory, service_name)

def cmd(command):
  call(command.split(' '))

def install_service(service_name, service_file):
  service_name = service_name.replace(' ', '')
  print('[SYS] > Install {} service'.format(service_name))
  insys_service_file = open('{}.service'.format(service_name), 'w')
  insys_service_file.write(service_file)
  insys_service_file.close()
  cmd('sudo mv {}.service /etc/systemd/system'.format(service_name))
  cmd('sudo chmod +x /etc/systemd/system/{}.service'.format(service_name))
  cmd('sudo systemctl enable {}'.format(service_name))
  cmd('sudo systemctl daemon-reload')
  cmd('sudo systemctl start {}'.format(service_name))
  # cmd('sudo systemctl status {}'.format(service_name))

def setup():
  # cmd('sudo apt-get install python3')

  cwd = os.getcwd()

  # Install main service
  cmd('sudo chmod +x ./startup')
  install_service('insys', generate_service_file('insys', 'startup', cwd))

  # Install update service
  cmd('sudo chmod +x ./update')
  cmd('sudo chmod +x ./update.py')
  install_service('insys_update', generate_service_file('insys_update', 'update', cwd))


if __name__ == "__main__":
  setup()