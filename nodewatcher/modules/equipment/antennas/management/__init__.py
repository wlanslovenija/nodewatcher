
from django import dispatch
from django.apps import apps
from django.db.models import signals as django_signals

from nodewatcher.core.generator.cgm import base as cgm_base
from nodewatcher.utils import loader

from .. import models as antennas_models

ANTENNA_FIXTURES_INSTALLED = False


@dispatch.receiver(
    django_signals.post_migrate,
    dispatch_uid='nodewatcher.modules.equipment.antennas.management.install_antenna_fixtures',
)
def install_antenna_fixtures(sender, **kwargs):
    """
    Installs fixtures for all registered internal antennas.
    """

    global ANTENNA_FIXTURES_INSTALLED
    if ANTENNA_FIXTURES_INSTALLED:
        return

    try:
        apps.get_model('antennas', 'Antenna')
    except LookupError:
        return

    # Ensure that all CGMs are registred
    loader.load_modules('cgm')

    for device in cgm_base.iterate_devices():
        for antenna in device.antennas:
            try:
                mdl = antennas_models.Antenna.objects.get(
                    internal_for=device.identifier,
                    internal_id=antenna.identifier,
                )
            except antennas_models.Antenna.DoesNotExist:
                mdl = antennas_models.Antenna(
                    internal_for=device.identifier,
                    internal_id=antenna.identifier,
                )

            # Update antenna model
            mdl.name = device.name
            mdl.manufacturer = device.manufacturer
            mdl.url = device.url
            mdl.polarization = antenna.polarization
            mdl.angle_horizontal = antenna.angle_horizontal
            mdl.angle_vertical = antenna.angle_vertical
            mdl.gain = antenna.gain
            mdl.save()

    ANTENNA_FIXTURES_INSTALLED = True
