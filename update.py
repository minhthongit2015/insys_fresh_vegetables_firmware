#!/usr/bin/python
# coding=utf-8
import requests
import datetime
import threading
import time
from subprocess import call
import argparse

def cmd(command):
  call(command.split(' '))

class Updater:
  def __init__(self, update_url, refresh_time=10):
    self.update_url = update_url
    self.refresh_time = refresh_time
    
    try:
      f = open('version.ini', 'r+')
      self.cur_version = f.read()
      print("[SYS] > Current firmware version: {}".format(self.cur_version))
    except:
      self.cur_version = ''
      pass
  
  def keep_up_date(self):
    # update_thread = threading.Thread(target=self.update)
    # update_thread.start()
    self.update()

  def update(self):
    while True:
      try:
        request = requests.get(self.update_url)
        self.resolveResult(request.text)
      except:
        pass
      time.sleep(self.refresh_time)
  
  def resolveResult(self, result):
    lines = result.split('\r\n')
    if len(lines) <= 0: return
    new_version = lines[0]
    if new_version <= self.cur_version: return

    print("[SYS] > Newer firmware found. Start installing newer version!")
    self.hard_update()

  def hard_update(self, new_version=''):
    cmd('git fetch --all')
    cmd('git reset --hard origin/master')
    cmd('sudo systemctl restart insys')
    fnew = open('version.ini', 'w')
    fnew.write(new_version if new_version != '' else self.cur_version)

if __name__ == "__main__":
  insys_updater = Updater("https://drive.google.com/uc?export=download&id=0B-_M0TAaeEKgY1ZjQ2lXQ2I5dkk", 30)

  parser = argparse.ArgumentParser(description='Update InSys firmware')
  parser.add_argument('-r', action='store_true', help='Hard update current firmware')

  args = parser.parse_args(['-h'])
  if args['r']:
    insys_updater.hard_update()
  else:
    insys_updater.keep_up_date()
