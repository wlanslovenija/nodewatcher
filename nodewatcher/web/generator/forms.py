from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from web.generator.models import Template, Profile
from web.nodes import ipcalc
from datetime import datetime
import re

IPV4_ADDR_RE = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')

class GenerateImageForm(forms.Form):
  """
  A simple form for image generation.
  """
  config_only = forms.BooleanField(initial = False, required = False, label = _("Configuration only"))
  email_user = forms.ModelChoiceField(
    User.objects.filter(is_active = True).order_by("username"),
    initial = User.objects.filter(is_active = True)[0].pk,
    required = False,
    label = _("Send image to"),
    empty_label = None
  )

  def clean(self):
    """
    Additional validation handler.
    """
    email_user = self.cleaned_data.get('email_user')

    if email_user and not email_user.email:
      raise forms.ValidationError(_("Specified user does not have an e-mail configured!"))

    return self.cleaned_data
  
  def save(self, request, node):
    """
    Returns user to which we will send the image.
    """
    if not request.user.is_staff() or not self.cleaned_data.get('email_user'):
      return node.owner
    else:
      return self.cleaned_data.get('email_user')
