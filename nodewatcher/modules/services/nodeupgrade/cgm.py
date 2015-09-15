from django.conf import settings

from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 900)
def nodeupgrade(node, cfg):
    """
    Configures nodeupgrade.
    """

    if getattr(settings, 'NODEUPGRADE_SERVER', None):
        nodeupgrade = cfg.nodeupgrade.add('nodeupgrade')
        nodeupgrade.server = settings.NODEUPGRADE_SERVER
        nodeupgrade.port = settings.NODEUPGRADE_PORT
        nodeupgrade.user = settings.NODEUPGRADE_USER

        # Install server's public key.
        public_key = cfg.crypto.add_object(
            cgm_base.PlatformCryptoManager.PUBLIC_KEY,
            settings.NODEUPGRADE_SERVER_PUBLIC_KEY,
            'server.nodeupgrade',
        )
        nodeupgrade.server_public_key = public_key.path()

        # Install authentication private key.
        private_key = cfg.crypto.add_object(
            cgm_base.PlatformCryptoManager.PRIVATE_KEY,
            settings.NODEUPGRADE_PRIVATE_KEY,
            'nodeupgrade',
            decoder=cgm_base.PlatformCryptoManager.BASE64,
        )
        nodeupgrade.private_key = private_key.path()

    # Ensure that nodeupgrade package is installed.
    cfg.packages.add('nodeupgrade')
