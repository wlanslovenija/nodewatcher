from django import apps


class ApiConfig(apps.AppConfig):
    name = 'nodewatcher.modules.frontend.api'
    label = 'frontend_api'
