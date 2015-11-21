from django.core.management import base as management_base
from django.contrib.auth import models as auth_models
from django.db import transaction

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
        with transaction.atomic(using=options.get('using', None)):
            for user in auth_models.User.objects.all():
                profile, created = models.UserProfileAndSettings.objects.get_or_create(user=user, using=options.get('using', None))
                if verbosity == 2 and created:
                    self.stdout.write('Created %s.\n' % profile)
