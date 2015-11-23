from django.core.management import base as management_base
from django.contrib.auth import models as auth_models
from django.db import transaction


class Command(management_base.NoArgsCommand):
    """
    This class defines an action for manage.py which assigns node maintainers group to all users missing it.
    """

    help = "Assign node maintainers group to all users missing it."

    def handle_noargs(self, **options):
        """
        Assigns node maintainers group to all users missing it.
        """

        verbosity = int(options.get('verbosity', 1))
        with transaction.atomic(using=options.get('using', None)):
            group = auth_models.Group.objects.get_by_natural_key(name="Node maintainers")

            for user in auth_models.User.objects.all():
                if not user.groups.filter(pk=group.pk).exists():
                    user.groups.add(group)
                    if verbosity >= 2:
                        self.stdout.write("Assigned to '%s'.\n" % user)
