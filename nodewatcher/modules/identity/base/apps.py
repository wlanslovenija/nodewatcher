from django import apps


class IdentityBaseConfig(apps.AppConfig):
    name = 'nodewatcher.modules.identity.base'
    label = 'identity_base'
