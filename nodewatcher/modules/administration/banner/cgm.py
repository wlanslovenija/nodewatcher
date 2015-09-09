import datetime

from django import template
from django.utils import timezone

from nodewatcher.core.registry import exceptions as registry_exceptions
from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 900)
def banner(node, cfg):
    """
    Configures a banner that will be displayed when logging in to
    the node.
    """

    # Get the node's local timezone using the location schema.
    try:
        node_zone = node.config.core.location().timezone or timezone.utc
    except (registry_exceptions.RegistryItemNotRegistered, AttributeError):
        node_zone = timezone.utc

    # Convert current timestamp to node-local time.
    now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(node_zone)

    # Obtain the device descriptor so we can include additional stuff into
    # the login banner by default.
    general = node.config.core.general()
    device = general.get_device()

    print device, getattr(device, 'manufacturer')
    banner_template = template.loader.get_template('banner/banner.txt')
    cfg.banner = banner_template.render(template.Context({
        'name': general.name,
        'uuid': node.uuid,
        'device_manufacturer': device.manufacturer,
        'device_name': device.name,
        'timestamp': now.strftime('%d.%m.%Y %H:%M:%S %Z'),
    }))

    # TODO: We currently cannot include the firmware version as configuration is generated before building.
