from django import apps
from django.core import management
from django.db.models import signals as models_signals


class AccountsConfig(apps.AppConfig):
    name = 'nodewatcher.extra.accounts'
    label = 'accounts'

    def createprofiles(self, **kwargs):
        management.call_command('createprofiles', **kwargs)

    def ready(self):
        super(AccountsConfig, self).ready()

        models_signals.post_migrate.connect(self.createprofiles, sender=self)

        # Register module signals.
        from . import signals
