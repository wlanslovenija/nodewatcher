import random
import inspect
import string

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.core import exceptions
from django.db import models
from django.forms import models as forms_models

def generate_random_password(length=8):
  """
  Generates a random password.
  """
  
  # Re-seed random number generator
  # This can make random values even more predictable if for seed
  # a time-dependent value is used as time of password generation
  # is easier to deduce than time of the first seed initialization
  # But Python uses os.urandom source if available so we are probably
  # better off
  random.seed()

  x = ''
  for i in xrange(0, length):
    x += random.choice(string.ascii_letters + string.digits)
  
  return x

def get_profile_model():
  """
  Gets user profile model based on AUTH_PROFILE_MODULE setting.
  
  Code based on `django.contrib.auth.models.User.get_profile`.
  """
  
  if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
    raise auth_models.SiteProfileNotAvailable('You need to set AUTH_PROFILE_MODULE in your project settings')
  try:
    app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
  except ValueError:
    raise auth_models.SiteProfileNotAvailable('app_label and model_name should be separated by a dot in the AUTH_PROFILE_MODULE setting')
  try:
    model = models.get_model(app_label, model_name)
    if model is None:
      raise auth_models.SiteProfileNotAvailable('Unable to load the profile model, check AUTH_PROFILE_MODULE in your project settings')
  except (ImportError, exceptions.ImproperlyConfigured):
    raise auth_models.SiteProfileNotAvailable
  return model

def user_activation_cleanup(user):
  """
  Some additinal clenaup after user activation.
  
  Currently it clears possible registration activation token.
  """
  
  if hasattr(user, 'registrationprofile_set'):
    from registration.models import RegistrationProfile
    try:
      profile = user.registrationprofile_set.get()
    except RegistrationProfile.DoesNotExist:
      # Registration profile does not exist anymore
      return
    # Just to be sure
    RegistrationProfile.objects.activate_user(profile.activation_key)
    # Not really sure why we would have to leave it as RegistrationProfile.ACTIVATED
    user.registrationprofile_set.all().delete()

def intersect(a, b):
  """
  Finds the intersection of two dictionaries.
  
  A key and value pair is included in the result only if the key exists in both given dictionaries. Value is taken from
  the second dictionary.
  """
  
  return dict(filter(lambda (x, y): x in a, b.items()))

def initial_accepts_request(request, form_class):
  """
  If fields in the given form uses dynamic initial values which accepts request argument it wraps them so that request is given
  to them when called.
  """
  
  initial = {}
  
  for name, field in form_class.base_fields.items():
    if callable(field.initial):
      try:
        if len(inspect.getargspec(field.initial)[0]) == 1:
          # We fight Python aliasing in for loops here
          initial[name] = (lambda fi: lambda: fi(request))(field.initial)
      except:
        pass
  
  if not initial:
    return form_class
  
  def wrapper(*args, **kwargs):
    initial.update(kwargs.get('initial', {}))
    kwargs['initial'] = initial
    return form_class(*args, **kwargs)
  
  return wrapper
