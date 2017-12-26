
from subprocess import call
import os
try: import configparser as cfg
except: import ConfigParser as cfg

from time import sleep

cmd = os.system

class Camera:
  def __init__(self, channel=""):
    self.config_path = 'config.cfg'
    self.cfg = cfg.ConfigParser()
    self.cfg.read(self.config_path)
    if 'Camera' not in self.cfg:
      self.cfg['Camera'] = {}
    self.channel = channel

  def save_cfg(self):
    with open(self.config_path, 'w') as f: self.cfg.write(f)

  @property
  def channel(self):
    return self.cfg['Camera']['channel']

  @channel.setter
  def channel(self, channel):
    self.cfg['Camera']['channel'] = channel # option value must be string!
    self.save_cfg()

  def start_streaming(self):
    cmd("raspivid -o - -t 0 -vf -hf -fps 30 -b 6000000 | ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv rtmp://a.rtmp.youtube.com/live2/{}".format(self.channel))

if __name__ == "__main__":
  camera = Camera("q1qt-c81f-05b8-5zqk")
  sleep(5)
  camera.start_streaming()