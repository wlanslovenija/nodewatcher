from django.contrib.auth import models as auth_models
from django.contrib.auth import backends as auth_backends
from django.contrib.sessions import models as sessions_models

import crypt
import md5crypt

try:
  import aprmd5
  APR_ENABLED = True
except ImportError:
  APR_ENABLED = False

class AprBackend(object):
  supports_object_permissions = False
  supports_anonymous_user = False
  supports_inactive_user = False

  def authenticate(self, username=None, password=None):
    """
    Authenticates against the database using Apache Portable Runtime MD5 hash function.
    """

    if not APR_ENABLED:
      return None

    try:
      user = auth_models.User.objects.get(username__iexact=username)
      if aprmd5.password_validate(password, user.password):
        # Successfully checked password, so we change it to the Django password format
        user.set_password(password)
        user.save()
        return user
    except ValueError:
      return None
    except auth_models.User.DoesNotExist:
      return None
  
  def get_user(self, user_id):
    """
    Translates the user ID into the User object.
    """
    try:
      return auth_models.User.objects.get(pk=user_id)
    except auth_models.User.DoesNotExist:
      return None

class CryptBackend(object):
  supports_object_permissions = False
  supports_anonymous_user = False
  supports_inactive_user = False

  def authenticate(self, username=None, password=None):
    """
    Authenticates against the database using crypt hash function.
    """
    try:
      user = auth_models.User.objects.get(username__iexact=username)
      if crypt.crypt(password, user.password) == user.password or md5crypt.md5crypt(password, user.password) == user.password:
        # Successfully checked password, so we change it to the Django password format
        user.set_password(password)
        user.save()
        return user
    except ValueError:
      return None
    except auth_models.User.DoesNotExist:
      return None
  
  def get_user(self, user_id):
    """
    Translates the user ID into the User object.
    """
    try:
      return auth_models.User.objects.get(pk=user_id)
    except auth_models.User.DoesNotExist:
      return None

class ModelBackend(auth_backends.ModelBackend):
  def authenticate(self, username=None, password=None):
    """
    Authenticates against the database using official implementation but catches exceptions and does it in case-insensitive manner.
    """
    try:
      user = auth_models.User.objects.get(username__iexact=username)
      if user.check_password(password):
        return user
    except ValueError:
      return None
    except auth_models.User.DoesNotExist:
      return None
