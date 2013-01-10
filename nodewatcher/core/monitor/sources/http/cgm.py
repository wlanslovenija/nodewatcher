from nodewatcher.core.generator.cgm import base as cgm_base

@cgm_base.register_platform_module("openwrt", 10)
def general(node, cfg):
    """
    Add HTTP monitoring packages to every node configuration.
    """
    cfg.packages.update(["nodewatcher-core", "nodewatcher-watchdog"])
