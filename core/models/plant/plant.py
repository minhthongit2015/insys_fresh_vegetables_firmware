

class Plant:
  """ Thông tin đầy đủ về cây trồng ở dạng đối tượng. Dữ liệu được nạp từ Plant Library. """
  def __init__(self, plant_name='', plant_type='', growth_stages=None):
    self.plant_name = plant_name
    self.plant_type = plant_type
    self.growth_stages = growth_stages