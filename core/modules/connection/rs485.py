
"""
RX / TX
"""
from core.modules.connection.my_serial import MySerial
import threading
from time import sleep

class RS485(MySerial):
  def __init__(self, port=['COM5','COM6','COM7', "/dev/ttyS0"], baudrate=19200, timeout=0.05, signature=b'#', terminator=b"\n"):
    """
    ``terminator``: bytes
    """
    super().__init__(port=port, baudrate=baudrate, timeout=timeout, signature=signature, terminator=terminator)
    self.STX = b'\x02'
    self.ETX = b'\x03'

  def _message_stream(self):
    print("[RS485] > Start message stream")
    message = b''
    buffer = b''
    is_start_frame = False
    while True:
      try:
        # đọc đến khi phát hiện frame
        buffer += self.serial.read_all()

        # Vòng lặp tách tất cả frame có trong buffer bỏ vào message để xử lý
        while len(buffer) > 0 and self.STX in buffer:
          # Nếu tín hiệu đã bắt đầu thì đọc đến khi gặp ký hiệu kết thúc
          if self.ETX in buffer:
            print("[RS485] > recv: {}".format(buffer))
            
            # Tách thông điệp ra khỏi frame đầu tiên trong buffer
            message += buffer[buffer.index(self.STX) + 1 : buffer.index(self.ETX)]
            # Đặt buffer về phần còn lại (có thể chứa các frame khác)
            buffer = buffer[buffer.index(self.ETX) + 3 : ] # bỏ qua checksum và \x00
            

            # tách package từ message, nếu chưa đủ package thì đợi tiếp
            while self.signature in message and self.terminator in message:
              package = message[message.index(self.signature) + len(self.signature) : message.index(self.terminator)] # Tách package đầu tiên
              message = message[message.index(self.terminator) + len(self.terminator) : ] # rest
              self._message_handler(package)
          else:
            break
      except Exception as e:
        # print("[RS485] > error: {}".format(e))
        is_start_frame = False
        message = b''
        buffer = b''
        pass
      sleep(0.005)

  def send(self, data):
    print("[RS485] > send package: {}".format(self.pack(data)), flush=True)
    if data not in self.send_queue:
      self.send_queue.append(data)
      self.notify_send()
  
  def pack(self, msg):
    return b'\x02' + super().pack(msg) + b'\x03' + self.calc_crc8(super().pack(msg))

  def calc_crc8(self, msg):
    crc = b'\x00'
    for c in msg:
      inbyte = c
      for i in range(8,0,-1):
        mix = (crc[0] ^ inbyte) & 0x01
        crc = bytes([crc[0] >> 1])
        if mix:
          crc = bytes([crc[0] ^ 0x8C])
        inbyte >>= 1
    return crc