#!/usr/bin/python3
# coding=utf-8

import requests
import datetime
import threading
import time
from subprocess import call
import argparse
from distutils.version import LooseVersion, StrictVersion

def cmd(command):
  call(command.split(' '))
  
def getFirmwareVersion():
  try:
    with open('version.ini', 'r+') as f:
      ver = f.read()
      return ver if ver != '' else '0.0.0.0'
  except:
    return '0.0.0.0'
    pass

class Updater:
  def __init__(self, update_url, refresh_time=10):
    self.update_url = update_url
    self.refresh_time = refresh_time
    
    try:
      f = open('version.ini', 'r+')
      self.cur_version = LooseVersion(f.read())
      f.close()
      print("[Updater] > Current firmware version: {}".format(self.cur_version.vstring))
    except:
      self.cur_version = LooseVersion('0.0.0.0')
  
  def keep_update(self):
    self.thread = threading.Thread(target=self.update)
    self.thread.start()
    self.thread.join()

  def update(self):
    while True:
      try:
        request = requests.get(self.update_url)
        self.resolveResult(request.text)
      except Exception as e:
        print(e)
        pass
      time.sleep(self.refresh_time)

  def resolveResult(self, result):
    lines = result.split('\r\n')
    if len(lines) <= 0: return
    new_version = LooseVersion(lines[0])
    print('[Updater] > Newest version: {}'.format(new_version.vstring))
    if new_version <= self.cur_version: return
    else:
      print("[Updater] > Newer firmware found. Start installing newer version!")
      print("[Updater] > Update from {} to {}".format(self.cur_version.vstring, new_version.vstring))
      self.cur_version = new_version
      self.hard_update()

  def hard_update(self):
    cmd('git fetch --all')
    cmd('git reset --hard origin/master')

    cmd('chmod +x ./setup.py')
    cmd('chmod +x ./uninstall.py')
    cmd('chmod +x ./startup')
    cmd('sudo systemctl restart insys.service')
    cmd('chmod +x ./update')
    cmd('chmod +x ./update.py')
    cmd('sudo systemctl restart insys_update.service')
    cmd('chmod +x ./core/modules/camera')
    cmd('sudo systemctl restart insys_camera.service')

if __name__ == "__main__":
  insys_updater = Updater("https://raw.githubusercontent.com/minhthongit2015/insys_fresh_vegetables_firmware/master/version.ini", 30)

  parser = argparse.ArgumentParser(description='InSys firmware updater')
  parser.add_argument('-r', action='store_true', help='Hard update current firmware')
  parser.add_argument('-v', action='store_true', help='View current version (version.ini)')

  args = parser.parse_args()
  if args.r:
    print('[Updater] > Hard update current firmware ({})'.format(insys_updater.cur_version.vstring))
    insys_updater.hard_update()
  elif args.v:
    print('[Updater] > Current Firmware Version: {}'.format(insys_updater.cur_version.vstring))
  else:
    print('[Updater] > InSys Updating Service Started Up!')
    print("[Updater] > Time: {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
    print("[Updater] > Firmware Version: {}".format(getFirmwareVersion()))
    insys_updater.keep_update()