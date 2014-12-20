from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 900)
def banner(node, cfg):
    """
    Configures a banner that will be displayed when logging in to
    the node.
    """

    cfg.banner = """
 +-------------------------------------------------+
 | nodewatcher                     nodewatcher.net |
 | v3 firmware                                     |
 +-------------------------------------------------+

"""
