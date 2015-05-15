from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 900)
def public_key_identity(node, cfg):
    """
    Configures public key identity on a node.
    """

    # Require the identity-pubkey package which will generate the node's key pair on first boot.
    cfg.packages.add('identity-pubkey')
