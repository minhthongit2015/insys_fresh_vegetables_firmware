# coding=utf-8

import datetime
import os
from time import time

class Logger:
  def __init__(self, log_name='', log_dir='.', time_format='%Y-%m-%d'):
    self.log_dir = log_dir
    self.log_name = log_name
    self.log_name_time_format = time_format
    self.flog = None
    self.logs = []
    self.envs_log = None
    os.makedirs(log_dir, exist_ok=True)

  def create_log_type(self, log_type, log_dir=''):
    if len(log_dir) <= 0: log_dir = self.log_dir
    new_log = {}
    new_log['type'] = log_type
    new_log['dir'] = log_dir
    if not os.path.exists(log_dir): os.makedirs(log_dir)
    self.logs.append(new_log)
    if log_type == 'envs': self.envs_log = new_log
    return new_log

  @staticmethod
  def log(record, file_name='', path='log', keep_open=False):
    if not os.path.exists(path): os.makedirs(path)
    with open("{}/{}_{}".format(path, file_name, Logger.today()), "a+") as fp:
      fp.write('{}\xc4{}\n'.format(round(time()), record))
      if keep_open: return fp
      else: fp.close()
  
  @staticmethod
  def get_log(file_name, path, hours_ago=6):
    records = []
    if not os.path.exists(path): return []
    else:
      today = Logger.today()
      pivot = time() - hours_ago*3600
      start = pivot
      pivot_date = Logger.pivot(start)
      while pivot_date <= today:
        with open("{}/{}_{}".format(path, file_name, pivot_date), "r") as fp: # today
          for line in fp:
            record_time, record_data = line[:-1].split("\xc4")
            if float(record_time) >= pivot:
              records.append([float(record_time), record_data]) # [time, record]
        start += 86400
        pivot_date = Logger.pivot(start)
      return records


  @staticmethod
  def pivot(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y_%m_%d')

  @staticmethod
  def today():
    return datetime.datetime.now().strftime('%Y_%m_%d')

  @staticmethod
  def today_obj():
    return datetime.datetime.fromtimestamp(time()-86400)

  @staticmethod
  def time():
    return datetime.datetime.now().strftime('%H:%M:%S')

  @staticmethod
  def date():
    return datetime.datetime.now().strftime('%Y/%m/%d')

  @staticmethod
  def datetime():
    return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')


