from django import apps, db
from django.core import management
from django.db.models import signals as models_signals


class AccountsConfig(apps.AppConfig):
    name = 'nodewatcher.extra.accounts'
    label = 'accounts'

    def create_profiles(self, **kwargs):
        management.call_command('createprofiles', **kwargs)

    def assign_default_permissions(self, **kwargs):
        management.call_command('assigndefaultpermissions', **kwargs)

    def ready(self):
        super(AccountsConfig, self).ready()

        models_signals.post_migrate.connect(self.create_profiles, sender=self)

        models_signals.post_migrate.connect(self.assign_default_permissions, sender=self)

        # Register other module signals.
        from . import signals
