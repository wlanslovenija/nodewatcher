from random import choice
from string import letters, digits

def generate_random_password(length = 20):
  """
  Generates a random password.
  """
  x = ''
  for i in xrange(0, length):
    x += choice(letters + digits)
  
  return x

