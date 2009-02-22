from django.db import models
from django.contrib.auth.models import User
from wlanlj.account.util import generate_random_password

class UserAccount(models.Model):
  """
  User account extension.
  """
  user = models.ForeignKey(User, unique = True)
  vpn_password = models.CharField(max_length = 50, null = True)
  name = models.CharField(max_length = 50, null = True)
  phone = models.CharField(max_length = 50, null = True)
  info_sticker = models.BooleanField(default = False, null = True)

  def generate_vpn_password(self):
    """
    Generates a new VPN password.
    """
    self.vpn_password = generate_random_password()
    self.save()

  @staticmethod
  def for_user(user):
    """
    Returns a profile for the selected user, generating it if it
    doesn't yet exist.
    """
    try:
      profile = user.get_profile()
    except UserAccount.DoesNotExist:
      profile = UserAccount(user = user)
      profile.generate_vpn_password()

    return profile

