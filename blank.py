import RPi.GPIO as GPIO
import serial
import time

RTSGPIO = 23

class RS485(serial.Serial):
   def __init__(self,
             port=None,
             baudrate=9600,
             bytesize=serial.EIGHTBITS,
             parity=serial.PARITY_NONE,
             stopbits=serial.STOPBITS_ONE,
             timeout=None,
             xonxoff=False,
             rtscts=False,
             write_timeout=None,
             dsrdtr=False,
             inter_byte_timeout=None,
             PinGpioRTS=None,
             rts_level_for_tx=True,
             rts_level_for_rx=False,
             loopback=False,
             delay_before_tx=None,
             delay_before_rx=None,
             **kwargs):
        self.PinGpioRTS = PinGpioRTS
        self.rts_level_for_tx = rts_level_for_tx
        self.rts_level_for_rx = rts_level_for_rx
        self.loopback = loopback
        self.delay_before_tx = delay_before_tx
        self.delay_before_rx = delay_before_rx
        if PinGpioRTS is not None:
             GPIO.setmode(GPIO.BCM)
             GPIO.setwarnings(False)
             GPIO.setup(PinGpioRTS,GPIO.OUT)
             self.setGpioRTS(self.rts_level_for_rx)
        super().__init__(port=port,baudrate=baudrate,bytesize=bytesize,
                         parity=parity,stopbits=stopbits,timeout=timeout,
                         xonxoff=xonxoff,rtscts=rtscts,write_timeout=write_timeout,
                         dsrdtr=dsrdtr,inter_byte_timeout=inter_byte_timeout)

   def setGpioRTS(self, value):
       if self.PinGpioRTS is not None:
          GPIO.output(self.PinGpioRTS,value)

   def  write(self,b):
       if self.PinGpioRTS is not None:
            # apply level for TX and optional delay
            self.setGpioRTS(self.rts_level_for_tx)
            if self.delay_before_tx is not None:
                time.sleep(self.delay_before_tx)
            # write and wait for data to be written
            super().write(b)
            super().flush()
            # optional delay and apply level for RX
            if self.delay_before_rx is not None:
                time.sleep(self.delay_before_rx)
            self.setGpioRTS(self.rts_level_for_rx)
       else:
            super().write(b)


ser = RS485(port='/dev/serial0',baudrate=9600,timeout=1,PinGpioRTS=RTSGPIO)
ser.flushInput()


while True:
    while ser.inWaiting() == 0:
        ser.write(b'B1')
        time.sleep(0.01)

    # read the data

    rcv_data = ser.readline()
    rcv_data_string = rcv_data.decode("utf-8")

    Count = int(rcv_data_string)
    Count = Count + 1

    print(Count)
    # send the value + 1

    ser.write((str(Count) + '\n').encode("utf-8"))

    if Count >= 1000:
        break
