from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from web.core.cgm import models as cgm_models
from web.registry import fields as registry_fields
from web.registry import forms as registry_forms
from web.registry import registration
from web.registry.cgm import base as cgm_base

class SolarPackageConfig(cgm_models.PackageConfig):
  """
  Common configuration for CGM packages.
  """
  # No fields
  
  class RegistryMeta(cgm_models.PackageConfig.RegistryMeta):
    registry_name = _("Solar")

registration.point("node.config").register_item(SolarPackageConfig)

@cgm_base.register_platform_package("openwrt", "nodewatcher-solar", SolarPackageConfig)
def solar_package(node, pkgcfg, cfg):
  """
  Configures the solar package for OpenWRT.
  """
  pass

