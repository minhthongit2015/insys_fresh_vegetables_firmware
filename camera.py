
from core.modules.config_mgr import ConfigManager

from subprocess import call
import os

from time import sleep

cmd = os.system

class Camera:
  def __init__(self):
    self.cfg = ConfigManager('CameraConfig')
    self.channel = self.cfg.getz('ytb_channel')

  def start_streaming(self):
    cmd("raspivid -o - -t 0 -vf -hf -fps 30 -b 6000000 | ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv rtmp://a.rtmp.youtube.com/live2/{} > /dev/null".format(self.channel))