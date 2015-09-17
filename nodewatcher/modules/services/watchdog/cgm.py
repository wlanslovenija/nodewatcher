from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 100)
def watchdog(node, cfg):
    """
    Enables the watchdog package.
    """

    cfg.packages.add('nodewatcher-watchdog')
