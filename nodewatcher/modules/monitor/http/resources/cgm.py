from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 50)
def resources(node, cfg):
    """
    Register packages needed for reporting resource data.
    """

    cfg.packages.update(['nodewatcher-agent-mod-resources'])
