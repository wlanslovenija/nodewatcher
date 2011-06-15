from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from web.core.cgm import models as cgm_models
from web.registry import fields as registry_fields
from web.registry import forms as registry_forms
from web.registry import registration
from web.registry.cgm import base as cgm_base

class CgmDigitempPackageConfig(cgm_models.CgmPackageConfig):
  """
  Common configuration for CGM packages.
  """
  # No fields
  
  class RegistryMeta(cgm_models.CgmPackageConfig.RegistryMeta):
    registry_name = _("Digitemp")

registration.point("node.config").register_item(CgmDigitempPackageConfig)

@cgm_base.register_platform_package("openwrt", "nodewatcher-digitemp", CgmDigitempPackageConfig)
def digitemp_package(node, pkgcfg, cfg):
  """
  Configures the digitemp package for OpenWRT.
  """
  pass

