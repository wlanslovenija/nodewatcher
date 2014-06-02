from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors
from nodewatcher.utils import ipaddr, loader

DATASTREAM_SUPPORTED = False
try:
    from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool
    DATASTREAM_SUPPORTED = True
except ImportError:
    pass

from . import events


class Interfaces(monitor_processors.NodeProcessor):
    """
    Stores interface monitoring data.
    """

    @monitor_processors.depends_on_context("http")
    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        # Fetch models for all existing interfaces and reset measured variables
        existing_interfaces = {}
        for iface in node.monitoring.core.interfaces():
            iface.tx_packets = None
            iface.rx_packets = None
            iface.tx_bytes = None
            iface.rx_bytes = None
            iface.tx_errors = None
            iface.rx_errors = None
            iface.tx_drops = None
            iface.rx_drops = None
            iface.mtu = None
            if isinstance(iface, monitor_models.WifiInterfaceMonitor):
                iface.mode = None
                iface.essid = None
                iface.bssid = None
                iface.channel = None
                iface.bitrate = None
                iface.rts_threshold = None
                iface.frag_threshold = None
                iface.signal = None
                iface.noise = None
                iface.snr = None

            existing_interfaces[iface.name] = iface

        version_ifaces = context.http.get_module_version("core.interfaces")
        version_wifi = context.http.get_module_version("core.wireless")
        if version_ifaces < 3 or version_wifi < 3 or context.http.get_version() < 3:
            return context

        interfaces = {}
        for name, data in context.http.core.interfaces.iteritems():
            if name.startswith('_') or name in ('lo',):
                continue

            try:
                iface = existing_interfaces[name]
            except KeyError:
                if name in context.http.core.wireless:
                    iface = node.monitoring.core.interfaces(create=monitor_models.WifiInterfaceMonitor)
                else:
                    iface = node.monitoring.core.interfaces(create=monitor_models.InterfaceMonitor)
                iface.name = name
                existing_interfaces[name] = iface

            self.process_interface(context, node, iface, data)
            iface.save()
            self.interface_enabled(context, node, iface)

            del existing_interfaces[name]
            interfaces[name] = iface

        # Store reset values for any interfaces that were not found; also hide these interfaces
        for iface in existing_interfaces.values():
            iface.save()
            self.interface_disabled(context, node, iface)

        # Check if any configured interfaces are missing from the report or if there are some
        # things misconfigured
        try:
            loader.load_modules('cgm')

            platform = node.config.core.general().platform
            if not platform:
                raise AttributeError
            device = node.config.core.general().get_device()

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

                    if iface_name not in interfaces:
                        # Generate an event that the interface is missing
                        events.MissingConfiguredInterface(node, iface_cfg, iface_name).post()
                    else:
                        iface_mon = interfaces[iface_name]

                        # Perform interface validation
                        if isinstance(iface_cfg, cgm_models.WifiInterfaceConfig):
                            # Check if interface type matches
                            if isinstance(iface_mon, monitor_models.WifiInterfaceMonitor):
                                # Check if mode matches
                                if iface_cfg.mode != iface_mon.mode:
                                    events.WifiInterfaceModeMismatch(node, iface_name, iface_cfg.mode, iface_mon.mode).post()

                                # Check if ESSID/BSSID matches
                                if iface_cfg.essid != iface_mon.essid:
                                    events.WifiInterfaceESSIDMismatch(node, iface_name, iface_cfg.essid, iface_mon.essid).post()

                                if iface_cfg.bssid != iface_mon.bssid:
                                    events.WifiInterfaceBSSIDMismatch(node, iface_name, iface_cfg.bssid, iface_mon.bssid).post()
                            else:
                                # Generate interface type mismatch event
                                events.InterfaceTypeMismatch(node, iface_cfg, iface_mon, iface_name).post()
                        else:
                            # TODO: Validation for other kinds of interfaces
                            pass
        except AttributeError:
            # Do no checking for routers without firmware configuration
            pass

        return context

    def process_interface(self, context, node, iface, data):
        """
        Performs per-interface processing.
        """

        # TODO: We currently assume that interfaces will not change types between wifi/non-wifi

        iface.hw_address = str(data.mac)
        iface.tx_packets = int(data.statistics.tx_packets)
        iface.rx_packets = int(data.statistics.rx_packets)
        iface.tx_bytes = int(data.statistics.tx_bytes)
        iface.rx_bytes = int(data.statistics.rx_bytes)
        iface.tx_errors = int(data.statistics.tx_errors)
        iface.rx_errors = int(data.statistics.rx_errors)
        iface.tx_drops = int(data.statistics.tx_dropped)
        iface.rx_drops = int(data.statistics.rx_dropped)
        iface.mtu = int(data.mtu) if data.mtu else None

        if iface.name in context.http.core.wireless:
            wdata = context.http.core.wireless[iface.name]

            # Wireless interface has some additional fields
            if wdata.mode == "Master":
                iface.mode = "ap"
            elif wdata.mode == "Ad-Hoc":
                iface.mode = "mesh"
            elif wdata.mode == "Client":
                iface.mode = "sta"
            else:
                iface.mode = None
                self.logger.warning("Ignoring unknown wifi mode '%s' on node '%s' interface '%s'!" % (wdata.mode, node.pk, iface.name))

            iface.essid = str(wdata.essid) if wdata.essid else None
            iface.bssid = str(wdata.bssid) if wdata.bssid else None
            iface.channel = int(wdata.channel) if wdata.channel else None
            iface.channel_width = int(wdata.channel_width) if wdata.channel_width else None
            iface.bitrate = float(wdata.bitrate) if wdata.bitrate else None
            iface.rts_threshold = int(wdata.rts_threshold) if wdata.rts_threshold else None
            iface.frag_threshold = int(wdata.frag_threshold) if wdata.frag_threshold else None
            iface.signal = int(wdata.signal) if wdata.signal else None
            iface.noise = int(wdata.noise) if wdata.noise else None
            # TODO: Calculate signal-to-noise ratio
            iface.snr = None
            iface.protocol = "".join(sorted(wdata.protocols)) if wdata.protocols else None

        if data.addresses:
            # Ensure that the interface is saved
            iface.save()

            existing_networks = {}
            for net in iface.networks.all():
                existing_networks[net.address] = net

            for network in data.addresses:
                address = ipaddr.IPNetwork("%(address)s/%(mask)d" % network)
                net = existing_networks.get(address, None)
                if net is None:
                    net, _ = iface.networks.get_or_create(
                        root=node,
                        interface=iface,
                        address=address
                    )
                    existing_networks[address] = net

                if network['family'] == 'ipv4':
                    net.family = 'ipv4'
                elif network['family'] == 'ipv6':
                    net.family = 'ipv6'
                else:
                    self.logger.warning("Unknown network family '%s' on node '%s' interface '%s'!" % (network.family, node.pk, iface.name))
                net.save()
                del existing_networks[address]

            for net in existing_networks.values():
                net.delete()

    def interface_enabled(self, context, node, iface):
        """
        Called when an interface has valid data (is available).
        """

        pass

    def interface_disabled(self, context, node, iface):
        """
        Called when an interface is no longer available.
        """

        pass


if DATASTREAM_SUPPORTED:
    class DatastreamInterfaces(Interfaces):

        def set_interface_hidden(self, iface, hidden):
            """
            Toggles hidden status of interface data.
            """

            descriptor = ds_pool.get_descriptor(iface)
            descriptor.tx_packets.set_tags(visualization={'hidden': hidden})
            descriptor.tx_packets_rate.set_tags(visualization={'hidden': hidden})
            descriptor.rx_packets.set_tags(visualization={'hidden': hidden})
            descriptor.rx_packets_rate.set_tags(visualization={'hidden': hidden})
            descriptor.tx_bytes.set_tags(visualization={'hidden': hidden})
            descriptor.tx_bytes_rate.set_tags(visualization={'hidden': hidden})
            descriptor.rx_bytes.set_tags(visualization={'hidden': hidden})
            descriptor.rx_bytes_rate.set_tags(visualization={'hidden': hidden})
            descriptor.tx_errors.set_tags(visualization={'hidden': hidden})
            descriptor.tx_errors_rate.set_tags(visualization={'hidden': hidden})
            descriptor.rx_errors.set_tags(visualization={'hidden': hidden})
            descriptor.rx_errors_rate.set_tags(visualization={'hidden': hidden})
            descriptor.tx_drops.set_tags(visualization={'hidden': hidden})
            descriptor.tx_drops_rate.set_tags(visualization={'hidden': hidden})
            descriptor.rx_drops.set_tags(visualization={'hidden': hidden})
            descriptor.rx_drops_rate.set_tags(visualization={'hidden': hidden})
            descriptor.mtu.set_tags(visualization={'hidden': hidden})

        def interface_enabled(self, context, node, iface):
            """
            Called when an interface has valid data (is available).
            """

            super(DatastreamInterfaces, self).interface_enabled(context, node, iface)
            self.set_interface_hidden(iface, False)

        def interface_disabled(self, context, node, iface):
            """
            Called when an interface is no longer available.
            """

            super(DatastreamInterfaces, self).interface_disabled(context, node, iface)
            self.set_interface_hidden(iface, True)
