from django import apps
from django.db.models import signals as models_signals

from . import permissions


class RegistryConfig(apps.AppConfig):
    name = 'nodewatcher.core.registry'

    def ready(self):
        super(RegistryConfig, self).ready()

        models_signals.post_migrate.connect(permissions.create_permissions)
