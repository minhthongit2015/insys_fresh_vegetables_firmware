
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
    try:
      super().read(self.config_file_path, encoding='utf-8')
    except:
      with open(self.config_file_path, 'w') as fp: fp.close()

  def set(self, key, value, section=''):
    if not section: section = self.section
    self.read()
    super().set(section, key, json.dumps(value, ensure_ascii=False))
    self.save()
  
  def getz(self, key, section=''):
    self.read()
    if not section: section = self.section
    try: value = super().get(section=section, option=key)
    except: return None
    return json.loads(value)

  def getc(self, key, section=''):
    if not section: section = self.section
    try: value = super().get(section=section, option=key)
    except: return None
    return json.loads(value)
  
  def save(self):
    with open(self.config_file_path, 'w') as fp:
      self.write(fp)
      fp.close()