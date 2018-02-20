# coding=utf-8
"""
"""

from core.firmware import InSysFirmware

if __name__ == "__main__":
  try:
    central_unit = InSysFirmware()
    central_unit.run()
  except KeyboardInterrupt:
    central_unit.shutdown()