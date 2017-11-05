# coding=utf-8

from firmware import InsysFirmware, getLocalDeviceId
from gardener import Gardener
from plant import Plant
from salad import *

if __name__ == "__main__":
  device = InsysFirmware(getLocalDeviceId('ID.txt'), [26,19,13,6], 4, 2, 300)
  device.run()

  gardener = Gardener(device, lazy=2)
  gardener.appendPlant(ButterheadLettuce())
  gardener.work()