

from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, XYZColor, xyYColor, LabColor, LuvColor, LCHuvColor, LCHabColor,\
                                    IlluminantMixin, ColorBase
import math

# Xây dựng thêm lớp HunterLab bổ xung cho thư viện
class HunterLabColor(IlluminantMixin, ColorBase):
    """
    Represents a CIE Hunter Lab color. For more information on CIE Lab,
    see `Lab color space <http://en.wikipedia.org/wiki/Lab_color_space>`_ on
    Wikipedia.
    """

    VALUES = ['lab_l', 'lab_a', 'lab_b']

    def __init__(self, lab_l, lab_a, lab_b, observer='2', illuminant='d65'):
        """
        :param float lab_l: L coordinate.
        :param float lab_a: a coordinate.
        :param float lab_b: b coordinate.
        :keyword str observer: Observer angle. Either ``'2'`` or ``'10'`` degrees.
        :keyword str illuminant: See :doc:`illuminants` for valid values.
        """
        super(HunterLabColor, self).__init__()
        #: L coordinate
        self.lab_l = float(lab_l)
        #: a coordinate
        self.lab_a = float(lab_a)
        #: b coordinate
        self.lab_b = float(lab_b)

        #: The color's observer angle. Set with :py:meth:`set_observer`.
        self.observer = None
        #: The color's illuminant. Set with :py:meth:`set_illuminant`.
        self.illuminant = None

        self.set_observer(observer)
        self.set_illuminant(illuminant)


"""
Các hàm chuyển đổi từ RGB sang CIE
"""

illuminant = 'd65' # chọn mức sáng là mức ánh sáng ban ngày

def RGB_XYZ(rgb):
  return convert_color(rgb, XYZColor, target_illuminant=illuminant)

def RGB_xyY(rgb):
  return convert_color(rgb, xyYColor, target_illuminant=illuminant)

def RGB_Lab(rgb):
  return convert_color(rgb, LabColor, target_illuminant=illuminant)

def RGB_Luv(rgb):
  return convert_color(rgb, LuvColor, target_illuminant=illuminant)

def RGB_LCHuv(rgb):
  return convert_color(rgb, LCHuvColor, target_illuminant=illuminant)

def RGB_LCHab(rgb):
  return convert_color(rgb, LCHabColor, target_illuminant=illuminant)

def RGB_Hunter(rgb):
  rgb_xyz = RGB_XYZ(rgb)
  x,y,z = (rgb_xyz.xyz_x*100, rgb_xyz.xyz_y*100, rgb_xyz.xyz_z*100)
  l = 10.0 * math.sqrt(y)
  a = 17.5 * ((1.02 * x) - y) / math.sqrt(y) if y != 0 else 0
  b = 7.0 * (y - (0.847 * z)) / math.sqrt(y) if y != 0 else 0
  return HunterLabColor(l, a, b)


"""
Ví dụ sử dụng chuyển đổi
"""
if __name__ == "__main__":
  rgb = sRGBColor(255, 0, 0, is_upscaled=True) # Màu cần chuyển đổi

  # Chuyển RGB sang XYZ
  rgb_xyz = RGB_XYZ(rgb)
  print("rgb ({}) -> xyz ({})".format(rgb, rgb_xyz))
  print(" ----------------------------------------------------------- ")

  # Chuyển RGB sang xyY
  rgb_xyY = RGB_xyY(rgb)
  print("rgb ({}) -> xyY ({})".format(rgb, rgb_xyY))
  print(" ----------------------------------------------------------- ")

  # Chuyển RGB sang LAB
  rgb_lab = RGB_Lab(rgb)
  print("rgb ({}) -> Lab ({})".format(rgb, rgb_lab))
  print(" ----------------------------------------------------------- ")

  # Chuyển RGB sang LUV
  rgb_luv = RGB_Luv(rgb)
  print("rgb ({}) -> LUV ({})".format(rgb, rgb_luv))
  print(" ----------------------------------------------------------- ")

  # Chuyển RGB sang LCHab
  rgb_LCHab = RGB_LCHab(rgb)
  print("rgb ({}) -> LCHab ({})".format(rgb, rgb_LCHab))
  print(" ----------------------------------------------------------- ")

  # Chuyển RGB sang LCHuv
  rgb_LCHuv = RGB_LCHuv(rgb)
  print("rgb ({}) -> LCHuv ({})".format(rgb, rgb_LCHuv))
  print(" ----------------------------------------------------------- ")

  # Chuyển RGB sang Hunter Lab
  rgb_hunter = RGB_Hunter(rgb)
  print("rgb ({}) -> Hunter Lab ({})".format(rgb, rgb_hunter))
  print(" ----------------------------------------------------------- ")
