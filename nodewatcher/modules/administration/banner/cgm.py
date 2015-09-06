import datetime

from django.utils import timezone

from nodewatcher.core.registry import exceptions as registry_exceptions
from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 900)
def banner(node, cfg):
    """
    Configures a banner that will be displayed when logging in to
    the node.
    """

    cfg.banner = """
                   _                         _          _
                  | |                       | |        | |
 _ __    ___    __| |  ___ __      __  __ _ | |_   ___ | |__    ___  _ __
| '_ \  / _ \  / _` | / _ \\ \ /\ / / / _` || __| / __|| '_ \  / _ \| '__|
| | | || (_) || (_| ||  __/ \ V  V / | (_| || |_ | (__ | | | ||  __/| |
|_| |_| \___/  \__,_| \___|  \_/\_/   \__,_| \__| \___||_| |_| \___||_|

    v3 firmware                                     nodewatcher.net

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
    cfg.banner += "        Node: %s\n" % general.name
    cfg.banner += "        UUID: %s\n" % node.uuid
    cfg.banner += "      Device: %s %s\n" % (device.manufacturer, device.name)
    cfg.banner += "  Configured: %s\n" % (now.strftime('%d.%m.%Y %H:%M:%S %Z'))
    cfg.banner += "\n"

    # TODO: We currently cannot include the firmware version as configuration is generated before building.
