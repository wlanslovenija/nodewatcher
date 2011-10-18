from django.db import models as django_models
from django.contrib.auth import models as auth_models

from web.account import utils
from web.nodes import models

class UserProfile(django_models.Model):
  """
  This class represents an user profile.
  """

  user = django_models.OneToOneField(auth_models.User, editable=False)

  vpn_password = django_models.CharField(max_length = 50, null = True)
  name = django_models.CharField(max_length = 50, null = True)
  phone = django_models.CharField(max_length = 50, null = True)
  info_sticker = django_models.BooleanField(default = False)
  project = django_models.ForeignKey(models.Project, null = True)
  developer = django_models.BooleanField(default = False)

  def generate_vpn_password(self):
    """
    Generates a new VPN password.
    """
    self.vpn_password = utils.generate_random_password()
    self.save()

  @staticmethod
  def for_user(user):
    """
    Returns a profile for the selected user, generating it if it
    doesn't yet exist.
    """
    try:
      profile = user.get_profile()
    except UserProfile.DoesNotExist:
      profile = UserProfile(user = user)
      profile.generate_vpn_password()

    return profile
