from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from wlanlj.generator.models import Template, Profile
from wlanlj.nodes import ipcalc
from datetime import datetime
import re

IPV4_ADDR_RE = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')

class GenerateImageForm(forms.Form):
  """
  A simple form for image generation.
  """
  config_only = forms.BooleanField(initial = False, required = False, label = _("Configuration only"))
  email_user = forms.ModelChoiceField(
    User.objects.filter(is_active = True),
    initial = User.objects.filter(is_active = True)[0].id,
    required = False,
    label = _("Send image to")
  )

  def clean(self):
    """
    Additional validation handler.
    """
    email_user = self.cleaned_data.get('email_user')

    if email_user and not email_user.email:
      raise forms.ValidationError(_("Specified user does not have an e-mail configured!"))

    return self.cleaned_data
  
  def save(self, node):
    """
    Saves modifiable stuff into the profile
    """
    return node.owner if not self.cleaned_data.get('email_user') else self.cleaned_data.get('email_user')

