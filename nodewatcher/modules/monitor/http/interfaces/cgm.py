from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 50)
def interfaces(node, cfg):
    """
    Register packages needed for reporting interface data.
    """

    cfg.packages.update([
        'nodewatcher-agent-mod-interfaces',
        'nodewatcher-agent-mod-wireless',
    ])
