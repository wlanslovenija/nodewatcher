from django import apps, db
from django.core import management
from django.contrib.auth import models as auth_models
from django.db.models import signals as models_signals


class AccountsConfig(apps.AppConfig):
    name = 'nodewatcher.extra.accounts'
    label = 'accounts'

    def create_profiles(self, **kwargs):
        management.call_command('createprofiles', **kwargs)

    def create_node_maintainers_group(self, **kwargs):
        try:
            # We try to create group object so that it always exist.
            group = auth_models.Group.objects.create(name="Node maintainers")

            # And assign the group "add_node" permission.
            permission = auth_models.Permission.objects.get_by_natural_key(codename='add_node', app_label='core', model='node')
            group.permissions.add(permission)
        except db.IntegrityError:
            pass
        except auth_models.Permission.DoesNotExist:
            pass

    def ready(self):
        super(AccountsConfig, self).ready()

        models_signals.post_migrate.connect(self.create_profiles, sender=self)

        models_signals.post_migrate.connect(self.create_node_maintainers_group, sender=self)

        # Register module signals.
        from . import signals
