from django.db import models
from django.contrib.auth.models import User
from ljwifi.account.util import generate_random_password

class UserAccount(models.Model):
  """
  User account extension.
  """
  user = models.ForeignKey(User, unique = True)
  vpn_password = models.CharField(max_length = 50, null = True)

  def generate_vpn_password(self):
    """
    Generates a new VPN password.
    """
    self.vpn_password = generate_random_password()
    self.save()

