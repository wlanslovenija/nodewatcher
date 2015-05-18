from django.utils import timezone

from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 900)
def banner(node, cfg):
    """
    Configures a banner that will be displayed when logging in to
    the node.
    """

    cfg.banner = """
 +-------------------------------------------------+
 | nodewatcher                     nodewatcher.net |
 | v3 firmware                                     |
 +-------------------------------------------------+

"""

    # Obtain the device descriptor so we can include additional stuff into
    # the login banner by default.
    general = node.config.core.general()
    device = general.get_device()
    cfg.banner += "        Node: %s\n" % general.name
    cfg.banner += "        UUID: %s\n" % node.uuid
    cfg.banner += "      Device: %s %s\n" % (device.manufacturer, device.name)
    cfg.banner += "  Configured: %s\n" % (timezone.now().strftime('%d.%m.%Y %H:%M:%S %Z'))
    cfg.banner += "\n"

    # TODO: We currently cannot include the firmware version as configuration is generated before building.

    # TODO: Datetime should probably be formatted based on the node's local timezone.
