from random import choice, seed
from string import ascii_letters, digits

def generate_random_password(length = 20):
  """
  Generates a random password.
  """
  
  # Re-seed random number generator
  # This can make random values even more predictable if for seed
  # a time-dependent value is used as time of password generation
  # is easier to deduce than time of the first seed initialization
  # But Python uses os.urandom source if available so we are probably
  # better off
  seed()

  x = ''
  for i in xrange(0, length):
    x += choice(ascii_letters + digits)
  
  return x
