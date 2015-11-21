from django.core import management
from django.core.management import base as management_base
from django.contrib.auth import models as auth_models
from django.db import transaction
from django.db.models import signals as models_signals

from ... import models


class Command(management_base.NoArgsCommand):
    """
    This class defines an action for manage.py which populates database with user profiles for all users missing them.
    """

    help = "Populate database with user profiles for all users missing them."

    def handle_noargs(self, **options):
        """
        Populates database with user profiles for all users missing them.
        """

        verbosity = int(options.get('verbosity', 1))
        with transaction.atomic():
            for user in auth_models.User.objects.all():
                profile, created = models.UserProfileAndSettings.objects.get_or_create(user=user)
                if verbosity == 2 and created:
                    self.stdout.write('Created %s.\n' % profile)


def command_signal(sender, app, created_models, **kwargs):
    if models.UserProfileAndSettings in created_models:
        management.call_command('createprofiles', **kwargs)

models_signals.post_syncdb.connect(command_signal, sender=models)
