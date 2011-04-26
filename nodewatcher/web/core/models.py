from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from registry import models as registry_models
from registry import fields as registry_fields
from registry import forms as registry_forms
from registry import registration

class GeneralConfig(registry_models.RegistryItem):
  """
  General node configuration containing basic parameters about the
  router type and the platform used.
  """
  project = registry_fields.ModelSelectorKeyField("nodes.Project")
  model = models.CharField(max_length = 20) # TODO fkey to router models
  platform = registry_fields.SelectorKeyField("core.general#platform")
  version = models.CharField(max_length = 20) # TODO fkey to versions (production, experimental, ...)
  timezone = models.CharField(max_length = 30)
  
  class RegistryMeta:
    form_order = 1
    registry_id = "core.general"
    registry_section = _("General Configuration")
    registry_name = _("Basic Configuration")

class GeneralConfigForm(forms.ModelForm):
  """
  General configuration form.
  """
  class Meta:
    model = GeneralConfig

registration.register_form_for_item(GeneralConfig, GeneralConfigForm)

# XXX this is just for testing selections
class ExtendedGeneralConfig(GeneralConfig):
  password = models.CharField(max_length = 30)
  
  class RegistryMeta(GeneralConfig.RegistryMeta):
    registry_name = _("Extended Configuration")

class ExtendedGeneralConfigForm(forms.ModelForm):
  class Meta:
    model = ExtendedGeneralConfig

registration.register_form_for_item(ExtendedGeneralConfig, ExtendedGeneralConfigForm)

class DoublyExtendedGeneralConfig(ExtendedGeneralConfig):
  krneki = models.CharField(max_length = 30)
  
  class RegistryMeta(ExtendedGeneralConfig.RegistryMeta):
    registry_name = _("Doubly Extended Configuration")

class VpnServerConfig(registry_models.RegistryItem):
  """
  Provides a VPN server specification that the nodes can use.
  """
  protocol = registry_fields.SelectorKeyField("core.vpn.server#protocol")
  hostname = models.CharField(max_length = 100)
  port = models.IntegerField()
  
  class RegistryMeta:
    form_order = 2
    registry_id = "core.vpn.server"
    registry_section = _("VPN Servers")
    registry_name = _("VPN Server")
    multiple = True

class VpnServerConfigForm(forms.ModelForm):
  """
  VPN server configuration form.
  """
  port = forms.IntegerField(min_value = 1, max_value = 49151)
  
  class Meta:
    model = VpnServerConfig

registration.register_form_for_item(VpnServerConfig, VpnServerConfigForm)

