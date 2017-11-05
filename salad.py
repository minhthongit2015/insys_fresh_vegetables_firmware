# coding=utf-8

"""
Dữ liệu trong salad.py chỉ gồm dữ liệu về cây, không dùng cho mục đích lập trình
"""

from plant import Plant, GrowthStage, WaterPoints
import pins

class Salad(Plant):
  def __init__(self, name, plantingDate, growthStages=[]):
    Plant.__init__(self, name, plantingDate, growthStages)

class ButterheadLettuce(Salad):
  """ Xà lách mỡ """
  def __init__(self):
    self.stage1 = GrowthStage(1, "Trồng trên trụ thủy canh", (1, 60), [
        WaterPoints('16:40,16:42,16:44,6:20,17:20', '1', .7)  # Tưới nước bón phân vào 6:20 và 17:20, mỗi lần 15p
      ])
    Salad.__init__(self, "Xà lách mỡ", (2,4,2017), [self.stage1])