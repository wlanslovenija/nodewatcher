from django import apps


class OAuthAuthenticationConfig(apps.AppConfig):
    name = 'nodewatcher.modules.authentication.oauth'
    label = 'authentication_oauth'


class OAuth2ProviderConfig(apps.AppConfig):
    name = 'oauth2_provider'
    verbose_name = 'Authentication: OAuth2'
