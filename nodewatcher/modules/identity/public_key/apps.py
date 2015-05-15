from django import apps


class PublicKeyConfig(apps.AppConfig):
    name = 'nodewatcher.modules.identity.public_key'
    label = 'identity_public_key'
