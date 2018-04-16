# coding=utf-8

try: import secrets
except: import core.modules.connection.secrets as secrets
from time import time

class Security:
  """
  """
  def __init__(self):
    self.read_security_code()
    self.tokens = { } # { "token": time }
    self.token_length = 12*2
  
  @property
  def isEnable(self):
    return self.security_code != ''

  def read_security_code(self):
    with open('./configs/security', 'r+') as fp:
      self.security_code = fp.read()
      fp.close()
      return self.security_code
  
  def save_security_code(self, security_code):
    with open('./configs/security', 'w+') as fp:
      fp.write(security_code)
      fp.close()
      self.security_code = security_code
  
  def check_security_code(self, security_code):
    return self.security_code == '' or security_code == self.security_code

  def check_token(self, token):
    now = time()
    if token in self.tokens:
      if self.tokens[token] - now > 86400*7: # expired in a week
        self.tokens.pop(token)
        return False
      else:
        return True
    else:
      return False

  def generate_token(self):
    token = secrets.token_hex(int(self.token_length/2))
    return token
  
  def allow_token(self, token):
    self.tokens[token] = time()