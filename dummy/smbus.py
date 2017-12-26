
class SMBus:
  def __init__(self, ver):
    print("[Simulation] > SMBus init SMBus({})".format(ver))
  
  def read_i2c_block_data(self, addr, offset, length):
    return [0,0,224,64]