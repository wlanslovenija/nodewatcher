from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 50)
def general(node, cfg):
    """
    Register packages needed for reporting via HTTP.
    """

    cfg.packages.update([
        'nodewatcher-agent',
        'nodewatcher-agent-mod-general',
    ])
