from nodewatcher.core.generator.cgm import base as cgm_base

from . import models


@cgm_base.register_platform_package('openwrt', 'nodewatcher-digitemp', models.DigitempPackageConfig)
def digitemp_package(node, pkgcfg, cfg):
    '''
    Configures the digitemp package for OpenWRT.
    '''

    pass
