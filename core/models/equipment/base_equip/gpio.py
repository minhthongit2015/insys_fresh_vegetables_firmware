# coding=utf-8

try: import RPi.GPIO as GPIO
except: import dummy.RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def clean():
  GPIO.cleanup()

class GPIOPin:
  def __init__(self, pin=None, is_output=True, default=False, reverse=False):
    self.pin = pin
    self.is_output = is_output
    self.default = default
    self.reverse = reverse # đảo ngược mức kích đầu ra
    self._on_high_listeners = []
    self._on_low_listeners = []
    self._on_data_listeners = []

  @property
  def pin(self):
    return self._pin

  @pin.setter
  def pin(self, pin):
    if pin is None:
      self._pin = None
    if pin < 0:
      print("[GPIOPin] > Warn: GPIO pin must set to an positive integer.")
      return
    else:
      self._pin = pin

    if self.is_output:
      GPIO.setup(self._pin, GPIO.OUT)
      GPIO.output(self._pin, GPIO.HIGH if self.default^self.reverse else GPIO.LOW)
    else:
      GPIO.setup(pin, GPIO.IN)

    self.oldState = self.state = self.default

  def read(self):
    return GPIO.input(self.pin)
  @property
  def value(self):
    return self.read()

  def addEventListener(self, event, callback):
    """
    ``event``: "high", "low", "both", "on", "off"
    """
    _event = ["high", "low", "both", "on", "off"]

    if event == "both":
      self._on_high_listeners.append(callback)
      self._on_low_listeners.append(callback)
      pin_event = GPIO.BOTH
    elif event == "high" or event == "on":
      self._on_high_listeners.append(callback)
      pin_event = GPIO.RISING
    elif event == "low" or event == "off":
      self._on_low_listeners.append(callback)
      pin_event = GPIO.FALLING

    if event in _event:
      GPIO.add_event_detect(self.pin, pin_event, callback=self._dispatch_event)
  
  def _dispatch_event(self, event):
    print(event)

  def high(self): # set pin to high
    return self.turn(True)
  def on(self):
    return self.high()
  
  def low(self): # set pin to low
    return self.turn(False)
  def off(self):
    return self.low()

  def set(self, state):
    # newState = self._verifyState(state)
    new_state = state
    self.old_state = self.state
    self.state = new_state
    if self.old_state^new_state:
      GPIO.output(self.pin, GPIO.HIGH if self.state^self.reverse else GPIO.LOW)
      # for eventDetect in self.eventDetect:
      #   if eventDetect: eventDetect(self)
      return True
    return False
  def turn(self, state):
    return self.set(state)

  def toggle(self):
    self.oldState = self.state
    self.state = not self.state
    self.set(self.state)
    return self.state