from nodewatcher.core.generator.cgm import base as cgm_base

from . import models

@cgm_base.register_platform_package("openwrt", "nodewatcher-solar", models.SolarPackageConfig)
def solar_package(node, pkgcfg, cfg):
    """
    Configures the solar package for OpenWRT.
    """
    pass
