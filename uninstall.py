#!/usr/bin/python3
# coding=utf-8

from subprocess import call
def cmd(command):
  call(command.split(' '))

cmd('sudo systemctl stop insys')
cmd('sudo systemctl stop insys_update')
cmd('sudo systemctl disable insys')
cmd('sudo systemctl disable insys_update')
cmd('sudo rm /etc/systemd/system/insys*')