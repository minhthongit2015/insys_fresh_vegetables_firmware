"""
#### Generate dummy value for pH Meter Module [3 -> 11]
"""
import random
import struct

class SMBus:
  def __init__(self, ver):
    print("[Simulation] > SMBus init SMBus({})".format(ver))
  
  def read_i2c_block_data(self, addr, offset, length):
    return struct.pack( 'f', random.uniform(3,11) )