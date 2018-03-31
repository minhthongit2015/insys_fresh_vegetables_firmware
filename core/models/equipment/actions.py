
"""
### Quản lý các hành động có thể của hệ thống phần cứng
- Tưới nước (mỗi trụ)
- Châm phân (mỗi trụ)
- Ánh sáng nhân tạo (mỗi trụ)
- Bật đèn hiệu tại trung tâm
- Bật đèn hiệu tại
"""

from core.models.equipment.base_equip.switch import Switch
from core.modules.logger import Logger
import json

class Action:
  def __init__(self, serial_port=None, default_reason='', action_name='', owner_station=None):
    self.owner_station = owner_station
    self.action_name = action_name
    self.default_reason = default_reason
    self.reasons = []
    self.start_listeners = {'*':[]} # { reason: [listener_array] }
    self.stop_listeners = {'*':[]}
    self._switch = Switch(name=action_name, serial_port=serial_port, owner_station=owner_station)

  def attach_serial_port(self, serial_port):
    self._switch.attach_serial_port(serial_port)
  
  def set_owner_station(self, station):
    self.owner_station = station
    self._switch.set_owner_station(station)

  @property
  def state(self):
    return self._switch.state

  def addEventListener(self, event='', listener=None, reason=''):
    """ Lắng nghe sự kiện ``event`` xảy ra bởi nguyên nhân ``reason``. Nếu ``reason`` để trống sẽ lắng nghe trên tất cả nguyên nhân."""
    if listener is None: return
    if reason is '': reason = '*'
    event_mapping = { "on": self.start_listeners,
                      "start": self.start_listeners,
                      'off': self.stop_listeners,
                      'stop': self.stop_listeners }
    if event in event_mapping:
      if reason not in event_mapping[event]:
        event_mapping[event][reason] = []
      if reason in event_mapping[event]:
        event_mapping[event][reason].append(listener)

  def _on(self, reason=''):
    if reason is '':
      if self.default_reason is not '':
        reason = self.default_reason
    if reason is not '' and reason not in self.reasons:
      self.reasons.append(reason)
      print("[Action:{}] > Adding reason \"{}\" to \"{}\" action. ({})".format(self.owner_station.id, reason, self.action_name, Logger.time()))
      if len(self.reasons) is 1:
        self._switch.on()
        self.on_started(reason)
        return True
    return False
  def on(self, reason_s=[]):
    rs = False
    if not reason_s: len(reason_s)
    elif 'str' in str(type(reason_s)):
      rs = self._on(reason_s)
    else:
      for reason in reason_s: rs = rs or self._on(reason)
    return rs
  def start(self, reason_s=[]):
    return self.on(reason_s)
  
  
  def _off(self, reason=''):
    if reason is '':
      if self.default_reason is not '':
        reason = self.default_reason
    if reason is not '':
      try:
        self.reasons.remove(reason)
        print("[Action:{}] > Remove reason \"{}\" from \"{}\" action. ({})".format(self.owner_station.id, reason, self.action_name, Logger.time()))
        if len(self.reasons) is 0:
          self._switch.off()
          self.on_stoped(reason)
          return True
      except: pass
    return False
  def off(self, reason_s=[]):
    rs = False
    if not reason_s: len(reason_s)
    elif 'str' in str(type(reason_s)):
      rs = self._off(reason_s)
    else:
      for reason in reason_s: rs = rs or self._off(reason)
    return rs
  def stop(self, reason_s=[]):
    return self.off(reason_s)

  def turn(self, state, reason_s=[]):
    if state: return self.on(reason_s)
    else: return self.off(reason_s)
  def set(self, state, reason_s=[]):
    return self.turn(state, reason_s)

  def on_started(self, reason=''):
    print("[Action:{}] > \"{}\" started cause \"{}\".".format(self.owner_station.id, self.action_name, reason), flush=True)
    if reason in self.start_listeners:
      for listener in self.start_listeners[reason]:
        listener(reason)
    for listener in self.start_listeners['*']:
      listener(reason)

  def on_stoped(self, reason=''):
    print("[{}] > \"{}\" stoped cause \"{}\".".format(self.owner_station.id, self.action_name, reason), flush=True)
    if reason in self.stop_listeners:
      for listener in self.stop_listeners[reason]:
        listener(reason)
    for listener in self.stop_listeners['*']:
      listener(reason)
  
  def clear_reasons(self):
    for reason in self.reasons:
      self._off(reason)

class WaterAction(Action):
  def __init__(self, serial_port=None, default_reason='', owner_station=None):
    super().__init__(serial_port, default_reason=default_reason, action_name='Water', owner_station=owner_station)

class NutrientAction(Action):
  def __init__(self, serial_port=None, default_reason='', owner_station=None):
    super().__init__(serial_port, default_reason=default_reason, action_name='Nutrient', owner_station=owner_station)

class LightAction(Action):
  def __init__(self, serial_port=None, default_reason='', owner_station=None):
    super().__init__(serial_port, default_reason=default_reason, action_name='Light', owner_station=owner_station)

class SignalAction(Action):
  def __init__(self, serial_port=None, signal_name='', default_reason='', owner_station=None):
    super().__init__(serial_port, default_reason=default_reason, action_name="Signal_{}".format(signal_name), owner_station=owner_station)

