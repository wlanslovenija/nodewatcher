from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from web.registry import models as registry_models
from web.registry import forms as registry_forms
from web.registry import registration

class GeneralConfig(registry_models.RegistryItem):
  """
  General node configuration containing basic parameters about the
  router type and the platform used.
  """
  model = models.CharField(max_length = 20) # TODO fkey to router models
  platform = models.CharField(max_length = 20, choices = registration.get_registered_choices("core.general#platform"))
  version = models.CharField(max_length = 20) # TODO fkey to versions (production, experimental, ...)
  
  class RegistryMeta:
    form_order = 1
    registry_id = "core.general"
    registry_name = _("General Configuration")

# TODO these registrations should be moved to core modules that implement them
registration.register_choice("core.general#platform", "openwrt", _("OpenWRT"))
registration.register_choice("core.general#platform", "ubnt", _("Ubiquiti AirOS"))

class GeneralConfigForm(forms.ModelForm):
  """
  General configuration form.
  """
  class Meta:
    model = GeneralConfig

registration.register_form_for_item(GeneralConfig, GeneralConfigForm)

class VpnServerConfig(registry_models.RegistryItem):
  """
  Provides a VPN server specification that the nodes can use.
  """
  protocol = models.CharField(max_length = 20, choices = registration.get_registered_choices("core.vpn.server#protocol"))
  hostname = models.CharField(max_length = 100)
  port = models.IntegerField()
  
  class RegistryMeta:
    form_order = 2
    registry_id = "core.vpn.server"
    registry_name = _("VPN Server")
    multiple = True

# TODO these registrations should be moved to core modules that implement them
registration.register_choice("core.vpn.server#protocol", "openvpn", _("OpenVPN"))

class VpnServerConfigForm(forms.ModelForm):
  """
  VPN server configuration form.
  """
  port = forms.IntegerField(min_value = 1, max_value = 49151)
  
  class Meta:
    model = VpnServerConfig

registration.register_form_for_item(VpnServerConfig, VpnServerConfigForm)

