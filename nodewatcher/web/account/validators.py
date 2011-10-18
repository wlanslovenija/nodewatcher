import socket

from django.core import exceptions
from django.core import validators
from django.utils.translation import ugettext_lazy as _

def validate_email_with_hostname(value):
  """
  Validator for e-mail addresses which does not only check for valid format but also checks for existence of e-mail address' hostname.
  """
  
  # First we run core e-mail validator
  validators.validate_email(value)
  # It seems it looks like e-mail address, let us check hostname
  if value and u'@' in value:
    parts = value.split(u'@')
    hostname_part = parts[-1]
    try:
      # Try to resolve it
      socket.getaddrinfo(hostname_part, None)
    except:
      try:
        # Try internationalized domain name
        hostname_part = hostname_part.encode('idna')
        socket.getaddrinfo(hostname_part, None)
        return
      except:
        pass
      raise exceptions.ValidationError(_(u'Enter a valid e-mail address.'), code='invalid')
