from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 50)
def clients(node, cfg):
    """
    Register packages needed for reporting wireless metadata.
    """

    cfg.packages.update(['nodewatcher-agent-mod-wireless'])
