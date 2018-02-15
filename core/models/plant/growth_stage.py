
"""
#### Thông tin giai đoạn sinh trưởng của cây trồng


**GrowthStage** - Quản lý thông tin các giai đoạn phát triển cây trồng
  * Thứ tự giai đoạn
  * Tên giai đoạn
  * Ngày bắt đầu và kết thúc của giai đoạn
  * Lịch trình tưới nước trong giai đoạn đó
"""
class GrowthStage:
  """ Thông tin 1 giai đoạn phát triển cây trồng """
  def __init__(self, stage_order=0, stage_name='', time_range=(), living_environment=None):
    self.stage_order = stage_order                # Số thứ tự của giai đoạn (1,2,3...)
    self.stage_name = stage_name                  # Tên giai đoạn phát triển (ươm mầm,...)
    self.start = time_range[0]                    # Ngày bắt đầu bước vào giai đoạn
    self.end = time_range[1]                      # Ngày kết thúc chuyển sang giai đoạn tiếp theo
    self.living_environment = living_environment  # Điều kiện môi trường để cây phát triển tốt