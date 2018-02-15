
from datetime import timedelta
import datetime

class TimePoint:
  """
  Lưu trữ mốc/khoảng thời gian để lập lịch cho một hành động nào đó.
  Hỗ trợ cho 2 chế độ lập lịch là:
  - Hành động vào một thời điểm cụ thể (VD: 6h15 sáng)
  - Hành động thực hiện sau mỗi một khoảng thời gian (VD: hành động mỗi 15p)
  """
  def __init__(self, time='', duration='', days=0, hours=0, minutes=0, seconds=0, every=''):
    """
    - ``time``: ``dd:hh:mm:ss`` Thời gian thực hiện hành động hay thời gian cách khoảng. (TimeDelta)
    - ``duration``: Thời lượng thực hiện hành động. (TimeDelta)
    - ``days``, ``hours``, ``minutes``, ``seconds``: Truyền số trực tiếp thay cho tham số time. (Number)
    - ``every``: Khoảng thời gian giữa 2 lần thực hiện hành động. (TimeDelta)
    """
    if time != '':
      parts = time.replace(' ', '').split(':')
      parts = list(map(lambda x: int(x), parts))
      if   len(parts) == 1:              minutes          = parts[0]
      elif len(parts) == 2:       hours, minutes          = parts
      elif len(parts) == 3:       hours, minutes, seconds = parts
      elif len(parts) == 4: days, hours, minutes, seconds = parts
      self.time = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
      self.start = self.time  # self.start is an alias of self.time
    else: self.start = self.time = None

    if duration != '':
      self.duration = TimePoint(duration).time
      if self.start:
        self.end = self.start + self.duration
      else: self.end = None
    else: self.end = self.duration = None

    if every != '':
      self.every = TimePoint(every).time
    else: self.every = None
  
  def __str__(self):
    return "start: %s\nduration: %s\nend: %s" % (str(self.start), str(self.duration), str(self.end))

class TimePointGroup:
  """ Wrapper của TimePoint
  - Giúp chuyển đổi từ dạng string kết hợp sang các đối tượng TimePoint riêng biệt
  VD:
  >>> "6:20, 17:20" sẽ chuyển thành 2 đối tượng TimePoint có cùng duration
  """
  def __init__(self, time_info='', duration='', every=''):
    self.duration = duration
    self.time_point_group = []
    if time_info != '':
      self.append_action_time(time_info.replace(' ','').split(','), False)
    if every != '':
      self.append_action_time(every.replace(' ','').split(','), True)
  
  def append_action_time(self, time_info='', every=False):
    if len(time_info) > 0:
      for time in time_info:
        if every: self.time_point_group.append(TimePoint(every=time, duration=self.duration))
        else: self.time_point_group.append(TimePoint(time=time, duration=self.duration))
  
  def is_time_for_action(self, start=None):
    now = datetime.datetime.now()
    dnow = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
    for time in self.time_point_group:
      if (time.start != None and time.end != None and time.start < dnow < time.end)\
       or (time.every != None and ((now-start) % time.every) <= time.duration):
        return True
    return False