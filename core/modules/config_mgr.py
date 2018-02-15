
try: import configparser as cfg
except: import ConfigParser as cfg
import json

class ConfigManager(cfg.ConfigParser):
  def __init__(self, section, config_file_path='./configs/config.cfg'):
    super().__init__()
    self.config_file_path = config_file_path
    self.read()
    self.section = section
    try: self.add_section(section)
    except: pass
    self.save()

  def read(self):
    super().read(self.config_file_path, encoding='utf-8')

  def set(self, key, value, section=''):
    if section != '': self.section = section
    self.read()
    self.set(self.section, key, json.dumps(value, ensure_ascii=False))
    self.save()
  
  def getz(self, key, section=''):
    self.read()
    if section != '': self.section = section
    return json.loads(super().get(section=self.section, option=key))
  
  def save(self):
    with open(self.config_file_path, 'w') as fp:
      self.write(fp)
      fp.close()