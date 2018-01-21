
import datetime
import os
from time import time

class Logger:
  def __init__(self, log_dir='.', log_name='', time_format='%Y-%m-%d'):
    self.log_dir = log_dir
    self.log_name = log_name
    self.log_name_time_format = time_format
    self.flog = None
    self.logs = []
    self.envs_log = None
    if not os.path.exists(log_dir): os.makedirs(log_dir)

  def create_log_type(self, log_type, log_dir=''):
    if len(log_dir) <= 0: log_dir = self.log_dir
    new_log = {}
    new_log['type'] = log_type
    new_log['dir'] = log_dir
    if not os.path.exists(log_dir): os.makedirs(log_dir)
    self.logs.append(new_log)
    if log_type == 'envs': self.envs_log = new_log
    return new_log

  def dump_record(self, log, data):
    now = datetime.datetime.now().strftime(self.log_name_time_format)
    flog = open("{}/{} {}.log".format(log['dir'], log['type'], now), "a+")
    flog.write("{} {}\n".format(int(time()), data))
    flog.close()

  def record(self, line, keep_open=False, log_name='', dump_time=True):
    """
    * `line`: string store information need to log
    * `keep_open`: keep the file open (to increse performance)
    * `log_name`: overwrite default log name file
    * `dump_time`: append timestamp to logfile or not (default is True)
    """
    now = datetime.datetime.now().strftime(self.log_name_time_format)
    if self.flog == None or log_name != '' or keep_open == False:
      if log_name != '': self.log_name = log_name
      self.flog = open("{}/{} {}.log".format(self.log_dir, self.log_name, now), "a+")

    time_now = datetime.datetime.now().strftime('[%H:%M:%S] ') if dump_time else ''
    self.flog.write('{}{}\n'.format(time_now, line))

    if not keep_open: self.flog.close()
    return self.flog

  def get_record_since(self):
    if not self.envs_log: return
    now = datetime.datetime.now().strftime(self.log_name_time_format)
    flog = open("{}/{} {}.log".format(self.log_dir, self.log_name, now), "r")
    pass

  def get_records_last_6h(self):
    if not self.envs_log: return
    try: flog = open("{}/{} {}.log".format(self.envs_log['dir'], self.envs_log['type'], datetime.datetime.now().strftime(self.log_name_time_format)), "r")
    except: return []
    last_6_hours = time() - 6*3600
    records = []
    for line in flog.readlines():
      record = line.split(" ")
      if int(record[0]) >= last_6_hours:
        records.append(record)
    flog.close()
    return records