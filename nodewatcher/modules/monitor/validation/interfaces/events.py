from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.events import declarative as events, pool
from nodewatcher.core.generator.cgm import models as cgm_models

# Need models to ensure that node.monitoring registration point is available
from nodewatcher.core.monitor import models as monitor_models


class MissingConfiguredInterface(events.NodeEventRecord):
    """
    An interface is configured but is missing.
    """

    iface_name = events.CharAttribute()

    def __init__(self, node, interface, iface_name):
        """
        Class constructor.

        :param node: Node on which the event ocurred
        :param interface: Configuration of the missing interface
        :param iface_name: The name of the missing interface
        """

        if isinstance(interface, cgm_models.EthernetInterfaceConfig):
            iface_type = 'ethernet'
        elif isinstance(interface, cgm_models.WifiInterfaceConfig):
            iface_type = 'wifi'
        else:
            iface_type = 'unknown'

        super(MissingConfiguredInterface, self).__init__(
            [node],
            events.NodeEventRecord.SEVERITY_WARNING,
            iface_type=iface_type,
            iface_name=iface_name,
        )

    @classmethod
    def get_description(cls, data):
        if data['iface_type'] == 'ethernet':
            msg = _("Ethernet interface '%(iface_name)s' is missing.")
        elif data['iface_type'] == 'wifi':
            msg = _("Wireless interface '%(iface_name)s' is missing.")
        else:
            msg = _("Unknown interface '%(iface_name)s' is missing.")

        return msg % data

pool.register_record(MissingConfiguredInterface)


class InterfaceTypeMismatch(events.NodeEventRecord):
    """
    An interface is configured but its monitored counterpart has a
    different type.
    """

    iface_name = events.CharAttribute()

    def __init__(self, node, interface_cfg, interface_mon, iface_name):
        """
        Class constructor.

        :param node: Node on which the event ocurred
        :param interface_cfg: Interface configuration
        :param interface_mon: Interface telemetry
        :param iface_name: The name of the interface
        """

        if isinstance(interface_cfg, cgm_models.EthernetInterfaceConfig):
            cfg_type = 'ethernet'
        elif isinstance(interface_cfg, cgm_models.WifiInterfaceConfig):
            cfg_type = 'wifi'

        if isinstance(interface_mon, monitor_models.WifiInterfaceMonitor):
            mon_type = 'ethernet'
        elif isinstance(interface_mon, monitor_models.InterfaceMonitor):
            mon_type = 'wifi'

        super(InterfaceTypeMismatch, self).__init__(
            [node],
            events.NodeEventRecord.SEVERITY_WARNING,
            iface_name=iface_name,
            cfg_type=cfg_type,
            mon_type=mon_type,
        )

    @classmethod
    def get_description(cls, data):
        type_msgs = {
            'ethernet': _("ethernet interface"),
            'wifi': _("wireless interface"),
        }

        return _("Interface type mismatch (%(cfg_type)s - %(mon_type)s).") % {
            'cfg_type': type_msgs[data['cfg_type']],
            'mon_type': type_msgs[data['mon_type']],
        }

pool.register_record(InterfaceTypeMismatch)


class WifiInterfaceESSIDMismatch(events.NodeEventRecord):
    """
    Wireless interface ESSID mismatch.
    """

    description = _("Wireless interface ESSID mismatch (%(essid_configured)s - %(essid_reported)s).")
    iface_name = events.CharAttribute()
    essid_configured = events.CharAttribute()
    essid_reported = events.CharAttribute()

    def __init__(self, node, iface_name, essid_configured, essid_reported):
        """
        Class constructor.

        :param node: Node on which the event ocurred
        :param iface_name: The name of the interface
        :param essid_configured: Configured ESSID
        :param essid_reported: Reported ESSID
        """

        super(WifiInterfaceESSIDMismatch, self).__init__(
            [node],
            events.NodeEventRecord.SEVERITY_WARNING,
            iface_name=iface_name,
            essid_configured=essid_configured,
            essid_reported=essid_reported,
        )

pool.register_record(WifiInterfaceESSIDMismatch)


class WifiInterfaceBSSIDMismatch(events.NodeEventRecord):
    """
    Wireless interface BSSID mismatch.
    """

    description = _("Wireless interface BSSID mismatch (%(bssid_configured)s - %(bssid_reported)s).")
    iface_name = events.CharAttribute()
    bssid_configured = events.CharAttribute()
    bssid_reported = events.CharAttribute()

    def __init__(self, node, iface_name, bssid_configured, bssid_reported):
        """
        Class constructor.

        :param node: Node on which the event ocurred
        :param iface_name: The name of the interface
        :param bssid_configured: Configured BSSID
        :param bssid_reported: Reported BSSID
        """

        super(WifiInterfaceBSSIDMismatch, self).__init__(
            [node],
            events.NodeEventRecord.SEVERITY_WARNING,
            iface_name=iface_name,
            bssid_configured=bssid_configured,
            bssid_reported=bssid_reported,
        )

pool.register_record(WifiInterfaceBSSIDMismatch)


class WifiInterfaceModeMismatch(events.NodeEventRecord):
    """
    Wireless interface mode mismatch.
    """

    description = _("Wireless interface mode mismatch (%(mode_configured)s - %(mode_reported)s).")
    iface_name = events.CharAttribute()
    mode_configured = events.ChoiceAttribute('node.config', 'core.interfaces#wifi_mode')
    mode_reported = events.ChoiceAttribute('node.config', 'core.interfaces#wifi_mode')

    def __init__(self, node, iface_name, mode_configured, mode_reported):
        """
        Class constructor.

        :param node: Node on which the event ocurred
        :param iface_name: The name of the interface
        :param mode_configured: Configured mode
        :param mode_reported: Reported mode
        """

        super(WifiInterfaceModeMismatch, self).__init__(
            [node],
            events.NodeEventRecord.SEVERITY_WARNING,
            iface_name=iface_name,
            mode_configured=mode_configured,
            mode_reported=mode_reported,
        )

pool.register_record(WifiInterfaceModeMismatch)


class WifiInterfaceChannelMismatch(events.NodeEventRecord):
    """
    Wireless interface channel mismatch.
    """

    description = _("Wireless interface channel mismatch (%(channel_configured)s - %(channel_reported)s).")
    iface_name = events.CharAttribute()
    channel_configured = events.CharAttribute()
    channel_reported = events.CharAttribute()

    def __init__(self, node, iface_name, channel_configured, channel_reported):
        """
        Class constructor.

        :param node: Node on which the event ocurred
        :param iface_name: The name of the interface
        :param channel_configured: Configured channel
        :param channel_reported: Reported channel
        """

        super(WifiInterfaceChannelMismatch, self).__init__(
            [node],
            events.NodeEventRecord.SEVERITY_WARNING,
            iface_name=iface_name,
            channel_configured=channel_configured,
            channel_reported=channel_reported,
        )

pool.register_record(WifiInterfaceChannelMismatch)
