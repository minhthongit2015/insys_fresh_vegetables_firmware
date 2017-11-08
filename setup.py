#!/usr/bin/python

from subprocess import call
import os
cwd = os.getcwd()

insys_service = """
# /etc/systemd/system

[Unit]
Description=INSYS FRESH VEGETABLES
After=multi-user.target

[Service]
Type=idle
ExecStart=/bin/bash {}/startup
WorkingDirectory={}
Restart=always

[Install]
WantedBy=multi-user.target
Alias=insys.service
""".format(cwd, cwd)

insys_update_service = """
# /etc/systemd/system

[Unit]
Description=INSYS FRESH VEGETABLES UPDATE SERVICE
After=multi-user.target

[Service]
Type=idle
ExecStart=/bin/bash {}/update.py
WorkingDirectory={}
Restart=always

[Install]
WantedBy=multi-user.target
Alias=insys_update.service
""".format(cwd, cwd)

def cmd(command):
  call(command.split(' '))

def install_service(service_name, service_file):
  insys_service_file = open('insys.service', 'w')
  insys_service_file.write(service_file)
  insys_service_file.close()
  cmd('sudo mv {}.service /etc/systemd/system'.format(service_name))
  cmd('sudo chmod +x /etc/systemd/system/{}.service'.format(service_name))
  cmd('sudo systemctl enable {}'.format(service_name))
  cmd('sudo systemctl daemon-reload')
  cmd('sudo systemctl start {}'.format(service_name))
  cmd('sudo systemctl status {}'.format(service_name))

def setup():
  # Install main service
  cmd('sudo chmod +x ./startup')
  install_service('insys', insys_service)

  # Install update service
  cmd('sudo chmod +x ./update.py')
  install_service('insys_update', insys_update_service)


if __name__ == "__main__":
  setup()