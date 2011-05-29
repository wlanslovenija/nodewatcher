from crypt import crypt

from django.contrib.auth import backends as auth_backends
from django.contrib.auth.models import User
from django.contrib.auth.models import check_password

if crypt('', '$1$DIF16...$Xzh7aN9GPHrZPK9DgggUK/') != '$1$DIF16...$Xzh7aN9GPHrZPK9DgggUK/':
  # crypt does not support MD5 hashed passwords, we will use Python implementation
  from md5crypt import unix_md5_crypt
  crypt = unix_md5_crypt

class NodewatcherBackend(auth_backends.ModelBackend):
  """
  Mildly augmented auth backend.
  """
  supports_anonymous_user = False
  supports_object_permissions = False
  
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
  
  def has_perm(self, user_obj, perm):
    """
    Returns True if the user has a specific permission. 
    """
    # Staff has complete access to anything
    if user_obj.is_staff:
      return True
    
    return super(NodewatcherBackend, self).has_perm(user_obj, perm)

