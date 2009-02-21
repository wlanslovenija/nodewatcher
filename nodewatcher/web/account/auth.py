from django.contrib.auth.models import User
import bcrypt

class CryptBackend:
  def authenticate(self, username = None, password = None):
    """
    Authenticate against the database using OpenBSD's blowfish crypt
    function.
    """
    try:
      user = User.objects.get(username = username)
      if bcrypt.hashpw(password, user.password) == user.password:
        return user
      else:
        return None
    except User.DoesNotExist:
      return None
    except ValueError:
      return None
  
  def get_user(self, user_id):
    """
    Translates the user id into a User object.
    """
    try:
      return User.objects.get(pk = user_id)
    except User.DoesNotExist:
      return None

