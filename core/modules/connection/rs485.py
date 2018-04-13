
"""
RX / TX
"""
from core.modules.connection.my_serial import MySerial
import threading
from time import sleep

class RS485(MySerial):
  def __init__(self, port=['COM5', "/dev/ttyS0"], baudrate=19200, timeout=0.05, terminator=b"\r\n"):
    """
    ``terminator``: bytes
    """
    super().__init__(port=port, baudrate=baudrate, timeout=timeout, terminator=terminator)
    self.STX = 2
    self.ETX = 3

  def _message_stream(self):
    message = b''
    while True:
      try:
        message += self.serial.read_all()
        if len(message) > 0 and self.STX in message and self.terminator in message:
          package = message.split(self.terminator)[0]
          message = message[len(package) + len(self.terminator): ] # rest
          if chr(package[0]) != '#': # if package is broken then just skip it
            continue
          self._message_handler(package[1:])
      except Exception as e:
        # print("[RS485] > error: {}".format(e))
        pass
      sleep(0.005)

  def send(self, data):
    print("[RS485] > Send: {}".format(data))
    self.send_queue.append(data)
    self.notify_send()
  
  def pack(self, msg):
    return b'\x02' + super().pack(msg) + b'\x03\x00'