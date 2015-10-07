from django.utils.translation import ugettext as _

from nodewatcher.core import models as core_models
from nodewatcher.core.generator.cgm import base as cgm_base

from . import models


@cgm_base.register_platform_package('openwrt', 'koruza-controller', models.KoruzaConfig)
def koruza(node, pkgcfg, cfg):
    """
    Configures the KORUZA controller unit.
    """

    try:
        pkgcfg = pkgcfg.get()
    except models.KoruzaConfig.MultipleObjectsReturned:
        raise cgm_base.ValidationError(_("Only one KORUZA controller may be defined."))

    # Get the peer's IP address.
    peer_ip = None
    try:
        # Use the first IPv4 Router ID.
        peer_ip = pkgcfg.peer_controller.config.core.routerid(queryset=True).filter(rid_family='ipv4')[0].router_id
    except (core_models.Node.DoesNotExist, AttributeError):
        pass
    except IndexError:
        raise cgm_base.ValidationError(_("Specified KORUZA controller peer does not have a router ID."))

    # Convert serial port.
    SERIAL_PORT_MAP = {
        'usb0': '/dev/ttyACM0',
        'usb1': '/dev/ttyACM1',
    }
    # TODO: Should we validate that the target device has USB support?

    try:
        serial_port = SERIAL_PORT_MAP[pkgcfg.serial_port]
    except KeyError:
        raise cgm_base.ValidationError(_("Unsupported serial port '%s' for KORUZA on OpenWrt.") % serial_port)

    # Install the KORUZA controller configuration file.
    cfg.files.install(
        '/etc/koruza.cfg',
        'irnas/koruza/koruza.cfg',
        context={
            'serial_port': serial_port,
            'peer_ip': peer_ip,
        },
    )

    # Install the KORUZA device reset script.
    cfg.files.install(
        '/etc/koruza/device_reset',
        'irnas/koruza/device_reset',
        mode=0755
    )

    cfg.packages.update([
        'koruza-controller',
        'lm4flash',
        'kmod-usb-acm'
    ])
