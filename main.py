# coding=utf-8

from core.firmware import InsysFirmware, getLocalDeviceId
from core.gardener import Gardener
from core.plant import Plant
from plants.salad import *

if __name__ == "__main__":
  device = InsysFirmware(getLocalDeviceId('ID.txt'), [26,19,13,6], 4, 2, 300)
  device.run()

  gardener = Gardener(device, lazy=2)
  gardener.appendPlant(ButterheadLettuce())
  gardener.work()