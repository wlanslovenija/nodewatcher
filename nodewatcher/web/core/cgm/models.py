from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from registry import fields as registry_fields
from registry import forms as registry_forms
from registry import registration

class CgmPackageConfig(registration.bases.NodeConfigRegistryItem):
  """
  Common configuration for CGM packages.
  """
  enabled = models.BooleanField(default = True)
  
  class RegistryMeta:
    form_order = 100
    registry_id = "core.packages"
    registry_section = _("Extra Packages")
    registry_name = _("Package Configuration")
    multiple = True
    hidden = True

registration.point("node.config").register_item(CgmPackageConfig)

