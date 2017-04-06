from django.core.management import base as management_base
from django.contrib.auth import models as auth_models
from django.db import transaction


class Command(management_base.BaseCommand):
    """
    This class defines an action for manage.py which assigns default permissions to all users missing them.
    """

    help = "Assign default permissions to all users missing them."

    def handle(self, **options):
        """
        Assigns default permissions to all users missing them.
        """

        verbosity = int(options.get('verbosity', 1))
        with transaction.atomic(using=options.get('using', None)):
            add_node_permission = auth_models.Permission.objects.get_by_natural_key(codename='add_node', app_label='core', model='node')

            for user in auth_models.User.objects.all():
                if add_node_permission not in user.user_permissions.all():
                    user.user_permissions.add(add_node_permission)
                    if verbosity >= 2:
                        self.stdout.write("Assigned 'core.add_node' to '%s'.\n" % user)
