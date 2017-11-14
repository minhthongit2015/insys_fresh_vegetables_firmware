# -*- coding: utf-8 -*-

"""
## Phân lớp module:
+ 1 ``Plant`` có nhiều ``GrowthStage``
+ 1 ``GrowthStage`` có nhiều ``WaterPoints``
+ 1 ``WaterPoints`` có nhiều ``WaterTime``
____________________________________

## Mô tả các module:
**Plant** - Quản lý thông tin cơ bản cây trồng
  * Tên
  * Các giai đoạn phát triển

**GrowthStage** - Quản lý thông tin các giai đoạn phát triển cây trồng
  * Thứ tự giai đoạn
  * Tên giai đoạn
  * Ngày bắt đầu và kết thúc của giai đoạn
  * Lịch trình tưới nước trong giai đoạn đó

**WaterPoints** - Quản lý các thời điểm tưới nước/bón phân
  * Các thời điểm tưới trong ngày
  * Thời gian tưới tương ứng
  * Lưu lượng tưới tương ứng

**WaterTime** - Thông tin thời điểm tưới trong ngày
  * Thời điểm bắt đầu và kết thúc
  * Kéo dài trong bao lâu
"""

from datetime import timedelta
import datetime

class c(timedelta):
  def print(self):
    print(self)

class WaterTime:
  """
  Lưu trữ thời gian tưới. Thời gian tưới có thể là mốc thời gian xác định hoặc là khoảng cách giữa các lần tưới
  """
  def __init__(self, time='', duration='', days=0, hours=0, minutes=0, seconds=0, every=''): # hh:mm:ss
    hour, minute, second = [0,0,0]
    if time != '':
      parts = time.replace(' ', '').split(':')
      parts = list(map(lambda x: int(x), parts))
      if len(parts) == 1:          minutes = parts[0]
      elif len(parts) == 2: hours, minutes = parts
      elif len(parts) == 3: hours, minutes, seconds = parts
      self.time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
      self.start = self.time  # alias
    else: self.start = self.time = None

    if duration != '':
      self.duration = WaterTime(duration).time
      if self.start:
        self.end = self.start + self.duration
      else: self.end = None
    else: self.end = self.duration = None

    if every != '':
      parts = every.replace(' ', '').split(':')
      parts = list(map(lambda x: int(x), parts))
      if len(parts) == 1:          minutes = parts[0]
      elif len(parts) == 2: hours, minutes = parts
      elif len(parts) == 3: hours, minutes, seconds = parts
      self.every = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    else: self.every = None
  
  def __str__(self):
    return "start: %s\nduration: %s\nend: %s" % (str(self.start), str(self.duration), str(self.end))

class WaterPoints:
  """ Thông tin 1 lần tưới trong ngày """
  def __init__(self, timeInfo='', duration='', amount=1, every=''):
    self.duration = duration  # Kéo dài bao lâu
    self.amount = amount      # Công suất tưới (hiện tại chưa điều khiển được công suất tưới)
    self.waterTimes = []
    if timeInfo != '':
      self.append_water_times(timeInfo.replace(' ','').split(','), False)
    if every != '':
      self.append_water_times(every.replace(' ','').split(','), True)
  
  def append_water_times(self, time_info='', every=False):
    if len(time_info) > 0:
      for water_time in time_info:
        if every:
          self.waterTimes.append(WaterTime(every=water_time, duration=self.duration))
        else:
          self.waterTimes.append(WaterTime(time=water_time, duration=self.duration))
  
  def is_time_for_water(self, start=None):
    now = datetime.datetime.now()
    dnow = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
    for waterTime in self.waterTimes:
      if (waterTime.start != None and waterTime.end != None and waterTime.start < dnow < waterTime.end) or (waterTime.every != None and ((now-start) % waterTime.every) <= waterTime.duration):
        return True
    return False

class GrowthStage:
  """ Thông tin 1 giai đoạn phát triển cây trồng """
  def __init__(self, stage, name, time_range, schedule=[]):
    self.stageName = name           # Tên giai đoạn
    self.stageNumber = stage        # Số thứ tự của giai đoạns
    self.start = time_range[0]      # Bắt đầu từ ngày thứ mấy
    self.end = time_range[1]        # Kết thúc vào ngày thứ mấy
    self.schedule = schedule        # Các thời điểm tưới trong ngày (WaterPoints)
  
  def water_if_in_stage(self, plant, pumb):
    start = plant.planting_date
    now = datetime.datetime.now()
    daypass = now - start
    if daypass.days >= self.start and daypass.days < self.end:
      for waterPoints in self.schedule:  # Duyệt qua tất cả các thời điểm tưới nước/bón phân trong ngày
        if waterPoints.is_time_for_water(start):
          if pumb and pumb.on():
            pumb.emitter(pumb)
          break
      else:
        if pumb and pumb.off():
          pumb.emitter(pumb)
      return True
    return False

class Plant:
  """ Thông tin cây trồng, nhiều giai đoạn phát triển """
  def __init__(self, name, planting_date, growth_stages=[]):
    self.name = name
    day,month,year = planting_date.split('/')
    self.planting_date = datetime.datetime(day=int(day), month=int(month), year=int(year))
    self.growth_stages = growth_stages