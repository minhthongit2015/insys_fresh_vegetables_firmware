
from core.models.gpio.gpio import Pin, ListPin
from core.modules.config_mgr import ConfigManager

class GPIOManager:
  """ Chưa sử dụng """
  def __init__(self):
    self.cfg = ConfigManager('GPIOConfig')
    self.list_gpio = self.cfg.get('GPIO')
    self.used_gpio = self.cfg.get('used')

  @property
  def remain(self):
    return len(self.list_gpio) - len(self.used_gpio)

  def take(self, name, number):
    if number > self.remain:
      print("[GPIOMGR] > not enough gpio! (remain: {})".format(self.remain))
      return None
    take_list = self.list_gpio[:number]
    self.used_gpio[name] = take_list
    self.list_gpio = self.list_gpio[number:]
    return take_list
