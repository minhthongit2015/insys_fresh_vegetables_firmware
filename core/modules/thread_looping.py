
import threading
from time import time, sleep

class ThreadLooping:
  """ Tạo thread và chạy vòng lặp dạng như Interval. Đảm bảo thời gian giữa 2 vòng là bằng nhau."""
  def __init__(self, target, wait_time=60, check_freq=0.5, args=(), kwargs={}):
    self.target = target
    self.wait_time = wait_time
    self.check_freq = check_freq
    self.args = args
    self.kwargs = kwargs
    self._running_flag = False

  def _loop(self):
    last = 0
    while self._running_flag:
      delta = time() - last
      wait_time_remaining = self.wait_time - delta
      while wait_time_remaining > 0:
        sleep(self.check_freq if wait_time_remaining > self.check_freq else wait_time_remaining)
        if not self._running_flag: return
        wait_time_remaining -= self.check_freq
      last = time()

      self.target(*self.args, **self.kwargs)

  def start(self):
    self._running_flag = True
    self.thread = threading.Thread(target=self._loop)
    self.thread.start()
  
  def stop(self):
    self._running_flag = False
    self.thread.join()