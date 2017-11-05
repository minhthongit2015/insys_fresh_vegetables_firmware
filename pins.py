import time
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setwarnings(False)

class Pin():
  def __init__(self, pin, isOutput=True, default=True, reverse=False, eventDetect=False, emitter=False): # Setup GPIO Pin for output by default
    self.pin = int(pin)
    self.default = self._verifyState(default)
    self.isOutput = self._verifyState(isOutput)
    self.oldState = self.state = self._verifyState(default)
    self.reverse = reverse
    self.setup(pin, isOutput, default)
    self.eventDetect = eventDetect
    self.emitter = emitter

  def setup(self, pin=-1, isOutput=False, default=True):
    if pin < 0:
      print("> Warn: GPIO pin must set to an positive integer.")
      return
    self.oldState = self.state = self.default
    if isOutput:
      GPIO.setup(pin, GPIO.OUT)
      GPIO.output(pin, GPIO.HIGH if default^self.reverse else GPIO.LOW)
    else:
      GPIO.setup(pin, GPIO.IN)

  def reset(self):
    self.setup(self.pin, self.isOutput, self.default)
  
  def onchange(self, eventDetect, phase=0):
    print("Setup onchange event on pin {} (phase: {})".format(self.pin, phase))
    if self.isOutput:
      self.eventDetect = eventDetect
    else:
      if phase == 1: event = GPIO.RISING
      elif phase == -1: event = GPIO.FALLING
      else: event = GPIO.BOTH
      GPIO.add_event_detect(self.pin, event, callback=eventDetect)

  def high(self): # set pin to high
    return self.turn(True)
  def on(self):
    return self.high()
  
  def low(self): # set pin to low
    return self.turn(False)
  def off(self):
    return self.low()

  def set(self, state):
    newState = self._verifyState(state)
    if self.state^newState:
      self.oldState = self.state
      self.state = newState
      GPIO.output(self.pin, GPIO.HIGH if self.state^self.reverse else GPIO.LOW)
      if self.eventDetect: self.eventDetect(self)
      return True
    return False
  def turn(self, state):
    return self.set(state)

  def toggle(self):
    self.oldState = self.state
    self.state = not self.state
    GPIO.output(self.pin, GPIO.HIGH if self.state^self.reverse else GPIO.LOW)
    if self.eventDetect: self.eventDetect(self)

  @property
  def value(self):
    return self.read()
  def read(self):
    return GPIO.input(self.pin)

  def _verifyState(self, state, default=False):
    try: state = int(state)
    except: return None
    return bool(state)

class ListPin():
  def __init__(self, pinList, isOut=[True], default=[True], reverse=[False], eventDetect=[False], emitter=[False]):
    self.size = len(pinList)
    self.pinList = pinList
    self.isOut = (isOut*self.size)[:self.size]
    self.default = (default*self.size)[:self.size]
    self.reverse = (reverse*self.size)[:self.size]
    self.eventDetect = (eventDetect*self.size)[:self.size]
    self.emitter = (emitter*self.size)[:self.size]
    self.pins = []
    for (pin, out, deft, rev, event, emit) in zip(self.pinList, self.isOut, self.default, self.reverse, self.eventDetect, self.emitter):
      self.pins.append(Pin(pin, out, deft, rev, event, emit))

  def setEventDetect(self, eventDetect=[False]):
    self.eventDetect = (eventDetect*self.size)[:self.size]
    for (pin, event) in zip(self.pins, self.eventDetect):
      pin.eventDetect = event