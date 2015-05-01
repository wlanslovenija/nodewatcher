from nodewatcher.core.generator.cgm import base as cgm_base

from . import models as pubkey_models


@cgm_base.register_platform_module('openwrt', 900)
def public_key_authentication(node, cfg):
    """
    Configures public key authentication on a node.
    """

    # Add network-wise authentication keys
    for global_key in pubkey_models.GlobalAuthenticationKey.objects.filter(enabled=True):
        cfg.crypto.add_object(
            cgm_base.PlatformCryptoManager.SSH_AUTHORIZED_KEY,
            global_key.public_key,
            global_key.pk,
        )

    # Add per-node configured authentication keys
    for auth in node.config.core.authentication(onlyclass=pubkey_models.PublicKeyAuthenticationConfig):
        cfg.crypto.add_object(
            cgm_base.PlatformCryptoManager.SSH_AUTHORIZED_KEY,
            auth.public_key.public_key,
            auth.pk,
        )
