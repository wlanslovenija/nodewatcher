from nodewatcher.core.generator.cgm import base as cgm_base

from . import models as pubkey_models


@cgm_base.register_platform_module('openwrt', 900)
def public_key_authentication(node, cfg):
    """
    Configures public key authentication on a node.
    """

    for auth in node.config.core.authentication(onlyclass=pubkey_models.PublicKeyAuthenticationConfig):
        key = cfg.keycfg.add('authorized_key')
        key.data = auth.public_key

    # Ensure that "keycfg" package is installed
    cfg.packages.update(['keycfg'])
