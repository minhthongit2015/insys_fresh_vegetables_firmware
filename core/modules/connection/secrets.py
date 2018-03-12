
import random

def token_hex(length):
  token = ''
  for i in range(length):
    token += hex(random.randint(0, 255))[-2:]
  return token

if __name__ == "__main__":
  test = token_hex(12)
  print(test)