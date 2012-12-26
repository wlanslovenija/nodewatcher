from django.conf import settings
from django.contrib.auth.management import create_permissions
from django.db import models

from south import signals as south_signals

from nodewatcher.core import antennas as core_antennas
from nodewatcher.registry.cgm import base as cgm_base

_core_migrated = False

def install_router_fixtures(sender, **kwargs):
    """
    Installs fixtures for all registered router models.
    """
    global _core_migrated
    if kwargs['app'] == "core":
        _core_migrated = True

    if not _core_migrated:
        return

    for router in cgm_base.iterate_routers():
        for antenna in router.antennas:
            try:
                mdl = core_antennas.Antenna.objects.get(internal_for = router.identifier, internal_id = antenna.identifier)
            except core_antennas.Antenna.DoesNotExist:
                mdl = core_antennas.Antenna(internal_for = router.identifier, internal_id = antenna.identifier)

            # Update antenna model
            mdl.name = router.name
            mdl.manufacturer = router.manufacturer
            mdl.url = router.url
            mdl.polarization = antenna.polarization
            mdl.angle_horizontal = antenna.angle_horizontal
            mdl.angle_vertical = antenna.angle_vertical
            mdl.gain = antenna.gain
            mdl.save()

def install_permissions(sender, **kwargs):
    """
    Installs permissions for all the applications. This is needed because it is not
    called by South, since it overrides post_syncdb signal.
    """
    create_permissions(models.get_app(kwargs['app']), set(), 0)

south_signals.post_migrate.connect(install_router_fixtures)
south_signals.post_migrate.connect(install_permissions)
