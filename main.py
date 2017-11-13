# coding=utf-8

from core.firmware import InsysFirmware, getLocalDeviceId
from core.gardener import Gardener
from core.plant import Plant
from core.plant_library import PlantLibrary

if __name__ == "__main__":
  try:
    device = InsysFirmware(getLocalDeviceId('ID.txt'), [26,19,13,6], [4, 0x04], 2, 300)
    device.run()

    plant_lib = PlantLibrary('./plants/vegetables.json')
    butterhead_lettuce = plant_lib.library[0]

    gardener = Gardener(device, lazy=2)
    gardener.appendPlant(butterhead_lettuce)
    gardener.work()
  except KeyboardInterrupt:
    device.clean()
    print("[SYS] >>> System shutdown!")