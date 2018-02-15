# coding=utf-8
"""
[Switch Pins]
 - 26: auto
 - 19: nutritive valve
 - 13: unused
 - 06: pump

[Signal Lights]
 - 12: System start normally
       Đèn sáng khi hệ thống khởi động bình thường, tất cả module đều hoạt động.
 - 16: Running mode (auto, manual, saving energy)
       Đèn sáng khi chế độ tự động bật
 - 20: Enviroment status
       Đèn sáng khi môi trường bất ổn (nhiệt độ cao, độ ẩm thấp, pH bất lợi...). Người dùng sẽ cần kiểm tra thông tin hoạt động để biết thêm chi tiết
 - 21: Network status
       Đèn sáng khi có kết nối internet tới server
"""

from core.firmware import InSysFirmware

if __name__ == "__main__":
  try:
    central_unit = InSysFirmware()
    central_unit.run()
  except KeyboardInterrupt:
    central_unit.shutdown()