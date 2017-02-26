from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors

from . import events


class InterfaceValidator(monitor_processors.NodeProcessor):
    """
    Stores interface monitoring data.
    """

    def cleanup(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        """

        # Check if any configured interfaces are missing from the report or if there are some
        # things misconfigured
        try:
            platform = node.config.core.general().platform
            device = node.config.core.general().get_device()
            if not platform or not device:
                raise AttributeError

            for interface in node.config.core.interfaces():
                if not interface.enabled:
                    continue

                iface_names = []
                if isinstance(interface, cgm_models.WifiRadioDeviceConfig):
                    for vif in interface.interfaces.all():
                        iface_names.append((vif, device.get_vif_mapping(platform, interface.wifi_radio, vif)))
                elif isinstance(interface, cgm_models.EthernetInterfaceConfig):
                    iface_names.append((interface, device.remap_port(platform, interface)))

                for iface_cfg, iface_name in iface_names:
                    if not iface_name:
                        continue

                    try:
                        iface_mon = node.monitoring.core.interfaces().get(name=iface_name)
                        # Interface is present.
                        events.MissingConfiguredInterface(node, iface_cfg, iface_name).absent()

                        # Perform interface validation
                        if isinstance(iface_cfg, cgm_models.WifiInterfaceConfig):
                            # Check if interface type matches
                            if isinstance(iface_mon, monitor_models.WifiInterfaceMonitor):
                                # Interface type matches.
                                events.InterfaceTypeMismatch(node, iface_cfg, iface_mon, iface_name).absent()

                                # Check if mode matches.
                                events.WifiInterfaceModeMismatch(node, iface_name, iface_cfg.mode, iface_mon.mode).post_or_absent(
                                    iface_cfg.mode != iface_mon.mode
                                )

                                # Check if ESSID matches.
                                events.WifiInterfaceESSIDMismatch(node, iface_name, iface_cfg.essid, iface_mon.essid).post_or_absent(
                                    iface_cfg.essid != iface_mon.essid
                                )

                                # In case it is configured, check if BSSID matches.
                                events.WifiInterfaceBSSIDMismatch(node, iface_name, iface_cfg.bssid, iface_mon.bssid).post_or_absent(
                                    iface_cfg.bssid and iface_cfg.bssid != iface_mon.bssid
                                )

                                # Check if channel matches.
                                wifi_device = iface_cfg.device
                                try:
                                    channel = device.get_radio(
                                        wifi_device.wifi_radio
                                    ).get_protocol(
                                        wifi_device.protocol
                                    ).get_channel(
                                        wifi_device.channel
                                    )
                                except AttributeError:
                                    channel = None

                                events.WifiInterfaceChannelMismatch(node, iface_name, channel.number, iface_mon.channel).post_or_absent(
                                    channel is not None and channel.number != iface_mon.channel
                                )
                            else:
                                # Generate interface type mismatch event
                                events.InterfaceTypeMismatch(node, iface_cfg, iface_mon, iface_name).post()
                        else:
                            # TODO: Validation for other kinds of interfaces
                            pass
                    except monitor_models.InterfaceMonitor.DoesNotExist:
                        # Generate an event that the interface is missing
                        events.MissingConfiguredInterface(node, iface_cfg, iface_name).post()
        except AttributeError:
            # Do no checking for routers without firmware configuration
            pass
