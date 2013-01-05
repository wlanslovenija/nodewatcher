# Here we augment South migrations

from django.contrib.auth.management import create_permissions
from django.db import models

from south import signals as south_signals

def install_permissions(sender, **kwargs):
    """
    Installs permissions for all the applications. This is needed because it is not
    called by South, since it overrides post_syncdb signal.
    """
    
    create_permissions(models.get_app(kwargs['app']), set(), 0)

south_signals.post_migrate.connect(install_permissions)
