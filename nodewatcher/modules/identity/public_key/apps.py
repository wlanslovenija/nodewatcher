from django import apps


class PublicKeyConfig(apps.AppConfig):
    name = 'nodewatcher.modules.identity.public_key'
    label = 'identity_public_key'

    def ready(self):
        # Connect to the HTTP context augmentation signal if HTTP source is installed.
        if apps.apps.is_installed('nodewatcher.modules.monitor.sources.http'):
            from . import http_signals
