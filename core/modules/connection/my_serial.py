
"""
RX / TX
"""
import serial
import threading
from time import sleep

class MySerial:
  def __init__(self, port=['COM4', 'COM5', 'COM6', "/dev/ttyS0"], baudrate=19200, timeout=0.05, signature=b'#', terminator=b"\r\n"):
    """
    ``terminator``: bytes
    """
    self.port = port
    self.baudrate = baudrate
    self.timeout = timeout
    self.terminator = terminator
    self.signature = signature
    self.listeners = []
    self.is_stated = False
    self.send_queue = []
  
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
    print("[Serial] > Start message stream")
    message = b''
    while True:
      try:
        message += self.serial.read_all()
        if len(message) > 0 and self.terminator in message:
          package = message.split(self.terminator)[0]
          message = message[len(package) + len(self.terminator): ] # rest
          if chr(package[0]) != '#': # if package is broken then just skip it
            continue
          self._message_handler(package[1:])
      except Exception as e:
        # print("[RS485] > error: {}".format(e))
        pass
      sleep(0.005)

  def _message_handler(self, message):
    message = message.decode('utf-8')
    for listener in self.listeners:
      listener(message)

  def send(self, data):
    print("[RS485] > Send: {}".format(data))
    self.send_queue.append(data)
    self.notify_send()
  
  def pack(self, msg):
    return self.signature + bytes(msg, 'utf-8') + self.terminator
  
  def notify_send(self):
    if len(self.send_queue) == 0:
      return
    try:
      msg = self.send_queue.pop(0)
      self.serial.write(self.pack(msg))
    except Exception as e:
      pass
    sleep(0.005)
    self.notify_send()