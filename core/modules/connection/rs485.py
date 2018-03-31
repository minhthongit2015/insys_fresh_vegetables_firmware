
"""
RX / TX
"""
import serial
import threading
from time import sleep

class RS485:
  def __init__(self, port=['COM5', "/dev/ttyS0"], baudrate=19200, timeout=0.05, terminator=b"\r\n"):
    """
    ``terminator``: bytes
    """
    self.port = port
    self.baudrate = baudrate
    self.timeout = timeout
    self.terminator = terminator
    self.listeners = []
    self.is_stated = False
  
  def open_port(self, port=None):
    if port == None:
      port = self.port
    if 'list' in str(type(port)):
      for p in port:
        try:
          self.serial = serial.Serial(p, baudrate=self.baudrate, timeout=self.timeout)
          break
        except Exception as e:
          # print("[RS485] > port {} is not available!")
          # print("[RS485] > error: {}".format(e))
          pass
      else:
        raise IOError("No port are available")
    else:
      self.serial = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)
  
  def start(self):
    try:
      self.open_port()
      self.message_resolve_thread = threading.Thread(target=self._message_stream)
      self.message_resolve_thread.start()
      self.is_stated = True
    except Exception as e:
      if not self.is_stated:
        print("[RS485] >> Failed to start! {}. Try after each 2 seconds...".format(e))
      self.is_stated = True
      sleep(2)
      self.start()

  def add_message_listener(self, listener):
    if listener not in self.listeners:
      self.listeners.append(listener)

  def _message_stream(self):
    while True:
      try:
        message = self.serial.read_until(self.terminator)
        if len(message) > 0:
          self._message_handler(message)
      except Exception as e:
        print("[RS485] > error: {}".format(e))

  def _message_handler(self, message):
    message = message.decode('utf-8')
    for listener in self.listeners:
      listener(message)

  def send(self, data):
    try:
      self.serial.write(bytes(data, 'utf-8') + self.terminator)
    except Exception as e:
      pass