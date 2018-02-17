

class ActionManager:
  def __init__(self, ):
    pass


"""
### Quản lý các hành động có thể của hệ thống phần cứng
- Tưới nước (mỗi trụ)
- Châm phân (mỗi trụ)
- Ánh sáng nhân tạo (mỗi trụ)
- Bật đèn hiệu tại trung tâm
- Bật đèn hiệu tại
"""

from core.models.gpio.gpio import Pin

import json

class Action:
  def __init__(self, pin, default_reason='', action_name=''):
    self.action_name = action_name
    self.default_reason = default_reason
    self.reasons = []
    self.start_listeners = {'*':[]} # { reason: [listener_array] }
    self.stop_listeners = {'*':[]}
    self._pin = pin # Pin object - must be setup at child class (WaterAction, NutrientAction...)
  
  @property
  def state(self):
    return self._pin.state
  
  def load(self, action_path):
    try:
      with open(action_path, 'r', encoding='utf-8') as fp:
        self.action_list = json.load(fp, encoding="utf-8")
      print("[ACTIONLIST] >> Plant library loaded.")
    except:
      print("[ACTIONLIST] >> Failed to load plant library ({})".format(action_path))

  def addEventListener(self, event='', listener=None, reason=''):
    """ Lắng nghe sự kiện ``event`` xảy ra bởi nguyên nhân ``reason``. Nếu ``reason`` để trống sẽ lắng nghe trên tất cả nguyên nhân."""
    if listener is None: return
    if reason is '': reason = '*'
    event_mapping = { "on": self.start_listeners,\
                      "start": self.start_listeners,\
                      'off': self.stop_listeners,\
                      'stop': self.stop_listeners }
    if event in event_mapping:
      if reason not in event_mapping[event]:
        event_mapping[event][reason] = []
      if reason in event_mapping[event]:
        event_mapping[event][reason].append(listener)

  def on(self, reason=''):
    if reason is '':
      if self.default_reason is not '':
        reason = self.default_reason
    if reason is not '' and reason not in self.reasons:
      self.reasons.append(reason)
      print("[Action] > Adding reason \"{}\" to \"{}\" action.".format(reason, self.action_name))
      if len(self.reasons) is 1:
        self._pin.on()
        self.on_started(reason)
        return True
    return False
  def start(self, reason=''):
    return self.on(reason)
  
  def off(self, reason=''):
    if reason is '':
      if self.default_reason is not '':
        reason = self.default_reason
    if reason is not '':
      try:
        self.reasons.remove(reason)
        print("[Action] > Remove reason \"{}\" from \"{}\" action.".format(reason, self.action_name))
        if len(self.reasons) is 0:
          self._pin.off()
          self.on_stoped(reason)
          return True
      except: pass
    return False
  def stop(self, reason=''):
    return self.off(reason)

  def turn(self, state, reason=''):
    if state: self.on(reason)
    else: self.off(reason)
  def set(self, state, reason=''):
    self.turn(state, reason)

  def on_started(self, reason=''):
    print("[Action] > \"{}\" started cause \"{}\".".format(self.action_name, reason), flush=True)
    if reason in self.start_listeners:
      for listener in self.start_listeners[reason]:
        listener(reason)
    for listener in self.start_listeners['*']:
      listener(reason)

  def on_stoped(self, reason=''):
    print("[Action] > \"{}\" stoped cause \"{}\".".format(self.action_name, reason), flush=True)
    if reason in self.stop_listeners:
      for listener in self.stop_listeners[reason]:
        listener(reason)
    for listener in self.stop_listeners['*']:
      listener(reason)

class WaterAction(Action):
  def __init__(self, pump_pin, default_reason=''):
    super().__init__(Pin(pump_pin, reverse=True), default_reason, 'Water')

class NutrientAction(Action):
  def __init__(self, valve_pin, default_reason=''):
    super().__init__(Pin(valve_pin, reverse=True), default_reason, 'Nutrient')

class LightAction(Action):
  def __init__(self, valve_pin, default_reason=''):
    super().__init__(Pin(valve_pin, reverse=True), default_reason, 'Light')

class SignalAction(Action):
  def __init__(self, signal_led_pin, signal_name='', default_reason=''):
    super().__init__(Pin(signal_led_pin), default_reason, "Signal_{}".format(signal_name))

