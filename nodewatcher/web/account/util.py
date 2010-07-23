from random import choice
from string import ascii_letters, digits

def generate_random_password(length = 20):
  """
  Generates a random password.
  """
  x = ''
  for i in xrange(0, length):
    x += choice(ascii_letters + digits)
  
  return x

