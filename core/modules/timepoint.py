# coding=utf-8

from datetime import timedelta
import datetime

class TimePoint:
  """
  Lưu trữ mốc/khoảng thời gian để lập lịch cho một hành động nào đó.
  Hỗ trợ cho 2 chế độ lập lịch là:
  - Hành động vào một thời điểm cụ thể (VD: 6h15 sáng)
  - Hành động thực hiện sau mỗi một khoảng thời gian (VD: hành động mỗi 15p)
  """
  def __init__(self, time=None, duration=None, days=0, hours=0, minutes=0, seconds=0, every=None, time_range=None):
    """
    - ``time``: ``dd:hh:mm:ss`` Thời gian thực hiện hành động hay thời gian cách khoảng. (TimeDelta)
    - ``duration``: Thời lượng thực hiện hành động. (TimeDelta)
    - ``days``, ``hours``, ``minutes``, ``seconds``: Truyền số trực tiếp thay cho tham số time. (Number)
    - ``every``: Khoảng thời gian giữa 2 lần thực hiện hành động. (TimeDelta)
    """
    self.time = self.start = self.every = self.duration  = None
    self.from_time = self.to_time = self.time_cycle = None

    # Hành động vào quãng thời gian xác định
    if time_range != None:
      parts = time_range.replace(' ', '').split('-')
      # ``time_cycle``: Bắt đầu từ from_time đến to_time mỗi ``time_cycle``
      # mỗi ``time_cycle`` có thể là mỗi ngày, mỗi tuần, mỗi tháng... Mặc định là mỗi ngày
      if len(parts) == 3:
        from_time, to_time, time_cycle = parts
        time_cycle = TimePoint.parse_timedelta(time_cycle)
      elif len(parts) == 2:
        from_time, to_time = parts
        time_cycle = TimePoint.parse_timedelta("24:00")
      
      self.from_time = TimePoint.parse_timedelta(from_time)
      self.to_time = TimePoint.parse_timedelta(to_time)
      self.time_cycle = time_cycle

    # Hành động vào thời điểm xác định
    if time != None:
      self.time = TimePoint.parse_timedelta(time)
      self.start = self.time  # self.start is an alias of self.time

    # Hành động cách nhau một quãng thời gian
    if every != None:
      self.every = TimePoint.parse_timedelta(every)
    
    # Hành động thực hiện theo thời điểm xác định ở trên kéo dài bao lâu
    if duration != None:
      self.duration = TimePoint.parse_timedelta(duration)
  
  @staticmethod
  def parse_timedelta(time):
    """ Chuyển thời gian dạng string sang timedelta để tính toán
      - 1 số:              phút
      - 2 số:        giờ : phút
      - 3 số:        giờ : phút : giây
      - 4 số: ngày : giờ : phút : giây
    """
    days, hours, minutes, seconds = 0,0,0,0
    parts = time.replace(' ', '').split(':')
    parts = list(map(lambda x: int(x), parts))
    if   len(parts) == 1:              minutes          = parts[0]
    elif len(parts) == 2:       hours, minutes          = parts
    elif len(parts) == 3:       hours, minutes, seconds = parts
    elif len(parts) == 4: days, hours, minutes, seconds = parts
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

class TimePointGroup:
  """ Wrapper của TimePoint
  - Giúp chuyển đổi từ dạng string kết hợp sang các đối tượng TimePoint riêng biệt
  VD:
  >>> "6:20, 17:20" sẽ chuyển thành 2 đối tượng TimePoint có cùng duration
  """
  def __init__(self, time_info='', duration='', every='', time_range=None):
    self.duration = duration
    self.time_point_group = []
    if time_range is not None:
      self.append_action_time(time_range=time_range)
    if time_info != '':
      self.append_action_time(time_info.replace(' ','').split(','), False)
    if every != '':
      self.append_action_time(every.replace(' ','').split(','), True)
  
  def append_action_time(self, time_info='', every=False, time_range=None):
    if time_range is not None:
      for t_range in time_range:
        self.time_point_group.append(TimePoint(time_range=t_range))
    
    if len(time_info) > 0:
      for time in time_info:
        if every: self.time_point_group.append(TimePoint(every=time, duration=self.duration))
        else: self.time_point_group.append(TimePoint(time=time, duration=self.duration))
  
  def is_time_for_action(self, start=None):
    now = datetime.datetime.now()
    dnow = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
    for time in self.time_point_group:
      if (time.start != None and time.duration != None and time.start <= dnow <= time.start + time.duration)\
       or (time.every != None and ((now-start) % time.every) <= time.duration)\
       or (time.from_time != None and time.to_time != None and time.time_cycle != None
           and ( time.from_time <= ((now-start) % time.time_cycle) <= time.to_time)):
        return True
    return False