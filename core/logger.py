
import datetime
import os

class Logger:
  def __init__(self, log_dir='.', log_name='', time_format='%Y-%m-%d'):
    self.log_dir = log_dir
    self.log_name = log_name
    self.log_name_time_format = time_format
    self.flog = None
    if not os.path.exists(log_dir): os.makedirs(log_dir)
    #'%Y/%m/%d %H:%M:%S'
  
  def record(self, line, keep_open=False, log_name='', dump_time=True):
    """
    * `line`: string store information need to log
    * `keep_open`: keep the file open
    * `log_name`: overwrite default log name file
    * `dump_time`: append timestamp to logfile or not (default is True)
    """
    now = datetime.datetime.now().strftime(self.log_name_time_format)
    if self.flog == None or log_name != '':
      if log_name != '': self.log_name = log_name
      self.flog = open("{}/{} {}.log".format(self.log_dir, self.log_name, now), "a+")

    time_now = datetime.datetime.now().strftime('[%H:%M:%S] ') if dump_time else ''
    self.flog.write('{}{}\r\n'.format(time_now, line))

    if not keep_open: self.flog.close()
    return self.flog

def main():
  logger = Logger("./log", "hutemp")
  pass

if __name__ == '__main__':
  main()