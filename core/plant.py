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

class WaterTime:
  def __init__(self, szTime='', szDuration='', days=0, hours=0, minutes=0, seconds=0): # hh:mm:ss
    hour, minute, second, start, duration, end = [0,0,0,None,None,None]
    if szTime != '':
      parts = szTime.replace(' ', '').split(':')
      parts = list(map(lambda x: int(x), parts))
      if len(parts) == 1:          minutes = parts[0]
      elif len(parts) == 2: hours, minutes = parts
      elif len(parts) == 3: hours, minutes, seconds = parts
      self.time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
      self.start = self.time  # alias
    if szDuration != '':
      self.duration = WaterTime(szDuration).time
      self.end = self.start + self.duration
  
  def __str__(self):
    return "start: %s\nduration: %s\nend: %s" % (str(self.start), str(self.duration), str(self.end))

class WaterPoints:
  """ Thông tin 1 lần tưới trong ngày """
  def __init__(self, timeInfo, duration, amount=1):
    self.duration = duration  # Kéo dài bao lâu
    self.amount = amount      # Công suất tưới (hiện tại chưa điều khiển được công suất tưới)
    timeInfo = timeInfo.replace(' ','').split(',')
    self.waterTimes = []
    for waterTime in timeInfo:
      self.waterTimes.append(WaterTime(waterTime, duration))
  
  def waterIfInTime(self, pumb=None):  # pumb : class Pin()
    now = datetime.datetime.now()
    now = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
    for waterTime in self.waterTimes:
      if waterTime.start < now < waterTime.end:
        if pumb and pumb.on():
          pumb.emitter(pumb)
        return
    if pumb and pumb.off():
      pumb.emitter(pumb)

class GrowthStage:
  """ Thông tin 1 giai đoạn phát triển cây trồng """
  def __init__(self, stage, name, timeRange, schedule=[]):
    self.stageName = name           # Tên giai đoạn
    self.stageNumber = stage        # Số thứ tự của giai đoạn
    self.start = timeRange[0]       # Bắt đầu từ ngày thứ mấy
    self.end = timeRange[1]         # Kết thúc vào ngày thứ mấy
    self.schedule = schedule        # Các thời điểm tưới trong ngày (WaterPoints)
    # for sch in schedule:
      

class Plant:
  """ Thông tin cây trồng, nhiều giai đoạn phát triển """
  def __init__(self, name, plantingDate, growthStages=[]):
    self.name = name
    self.plantingDate = plantingDate
    self.growthStages = growthStages