from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from web.core.cgm import models as cgm_models
from web.registry import fields as registry_fields
from web.registry import forms as registry_forms
from web.registry import registration
from web.registry.cgm import base as cgm_base

class CgmSolarPackageConfig(cgm_models.CgmPackageConfig):
  """
  Common configuration for CGM packages.
  """
  serial_port = models.CharField(max_length = 30)
  
  class RegistryMeta(cgm_models.CgmPackageConfig.RegistryMeta):
    registry_name = _("Solar")

registration.point("node.config").register_item(CgmSolarPackageConfig)

@cgm_base.register_platform_package("openwrt", "solar", CgmSolarPackageConfig)
def solar_package(node, pkgcfg, cfg):
  """
  Configures the solar package for OpenWRT.
  """
  pass

