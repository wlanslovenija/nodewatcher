from django import apps


class HmacConfig(apps.AppConfig):
    name = 'nodewatcher.modules.identity.hmac'
    label = 'identity_hmac'

    def ready(self):
        # Connect verification signals.
        from . import signals

        # Connect to the HTTP context augmentation signal if HTTP source is installed.
        if apps.apps.is_installed('nodewatcher.modules.monitor.sources.http'):
            from . import http_signals
