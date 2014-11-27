from django import apps


class PublicKeyConfig(apps.AppConfig):
    name = 'nodewatcher.modules.authentication.public_key'
    label = 'public_key'
    verbose_name = 'Authentication: Public Key'
