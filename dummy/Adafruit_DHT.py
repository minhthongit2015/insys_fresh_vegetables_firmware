"""
#### Generate dummy value for Hutemp Module
* Humidity: [45 -> 100]
* Temperature: [20 -> 35]
"""
import random

DHT22 = 3

def read_retry(*args):
  return read()

def read(*args):
  # return (80, 20)
  return (round(random.uniform(45,100), 2), round(random.uniform(20,35), 2))