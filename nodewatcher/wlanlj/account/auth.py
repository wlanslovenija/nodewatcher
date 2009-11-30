from django.contrib.auth.models import User
from django.contrib.auth.models import check_password
from crypt import crypt

if crypt('', '$1$DIF16...$Xzh7aN9GPHrZPK9DgggUK/') != '$1$DIF16...$Xzh7aN9GPHrZPK9DgggUK/':
  # crypt does not support MD5 hashed passwords, we will use Python implementation
  from md5crypt import unix_md5_crypt
  crypt = unix_md5_crypt

class CryptBackend:
  def authenticate(self, username = None, password = None):
    """
    Authenticate against the database using OpenBSD's blowfish crypt
    function.
    """
    try:
      user = User.objects.get(username = username)
      if check_password(password, user.password):
        # Successfully checked password in Django password format, so we can change it to crypt format
        salt = '$1$' + User.objects.make_random_password(8)
        user.password = crypt(password, salt)
        user.save()
    except ValueError:
      pass
    except User.DoesNotExist:
      return None

    try:
      if crypt(password, user.password) == user.password and user.is_active:
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
