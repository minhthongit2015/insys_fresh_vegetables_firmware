
class Switch():
  def __init__(self, name="", serial_port=None, default=False, owner_station=None):
    self.name = name
    self.serial_port = serial_port
    self.owner_station = owner_station
    self.old_state = self.state = default
  
  def attach_serial_port(self, serial_port):
    self.serial_port = serial_port
  
  def set_owner_station(self, station):
    self.owner_station = station

  def on(self):
    if self.serial_port:
      self.serial_port.on(self.owner_station, self)

  def off(self):
    if self.serial_port:
      self.serial_port.off(self.owner_station, self)

