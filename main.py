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

from core.firmware import InsysFirmware, getLocalDeviceId
from core.gardener import Gardener
from core.plant import Plant
from core.plant_library import PlantLibrary

if __name__ == "__main__":
  try:
    plant_lib = PlantLibrary('./plants/vegetables.json')
    butterhead_lettuce = plant_lib.plant_parse(plant_lib.library[0])

    device = InsysFirmware(getLocalDeviceId('ID.txt'), [26,19,13,6], [4, 0x04], [17,27,22,10,9], 5, 300)
    device.run()

    gardener = Gardener(device, water_freq_time=2)
    gardener.appendPlant(butterhead_lettuce)
    gardener.work()

    device.startWebsocketServer()

    device.join()
    gardener.join()
  except KeyboardInterrupt:
    device.clean()
    print("[SYS] >>> System shutdown!")