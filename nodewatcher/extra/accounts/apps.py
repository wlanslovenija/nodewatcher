from django import apps
from django.core import management
from django.db.models import signals as models_signals


def command_signal(sender, **kwargs):
    management.call_command('createprofiles', **kwargs)


class AccountsConfig(apps.AppConfig):
    name = 'nodewatcher.extra.accounts'
    label = 'accounts'

    def ready(self):
        super(AccountsConfig, self).ready()

        models_signals.post_migrate.connect(command_signal, sender=self)

        # Register module signals.
        from . import signals
