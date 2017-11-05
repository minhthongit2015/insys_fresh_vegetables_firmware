# coding=utf-8
import requests
import datetime
import threading
import time
from subprocess import call


class Updater:
  def __init__(self, update_url, install_path, refresh_time=10):
    self.update_url = update_url
    self.refresh_time = refresh_time
    self.install_path = install_path
    
    try:
      f = open('version.ini', 'r+')
      self.curversion = f.read()
      print("[SYS] > Current version: {}".format(self.curversion))
    except:
      self.curversion = ''
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
    if new_version <= self.curversion: return

    call('sudo systemctl stop insys'.split(' '))
    for line in lines:
      part = line.split(" ")
      new_file = requests.get(part[1]).text
      f = open("{}/{}".format(self.install_path, part[0]), 'w')
      f.write(new_file)
      f.close()


if __name__ == "__main__":
  insys_updater = Updater("https://drive.google.com/uc?export=download&id=0B-_M0TAaeEKgY1ZjQ2lXQ2I5dkk",
    '/home/pi/Desktop/INSYS', 30)
  insys_updater.keep_up_date()
