from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors

DATASTREAM_SUPPORTED = False
try:
    from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool
    DATASTREAM_SUPPORTED = True
except ImportError:
    pass


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
        if version_ifaces < 2 or version_wifi < 2:
            return context

        for name, data in context.http.iface.iteritems():
            try:
                iface = existing_interfaces[name]
            except KeyError:
                if name in context.http.wireless.radios:
                    iface = node.monitoring.core.interfaces(create=monitor_models.WifiInterfaceMonitor)
                else:
                    iface = node.monitoring.core.interfaces(create=monitor_models.InterfaceMonitor)
                iface.name = name
                existing_interfaces[name] = iface

            self.process_interface(context, iface, data)
            iface.save()
            self.interface_enabled(context, iface)

            del existing_interfaces[name]

        # Store reset values for any interfaces that were not found; also hide these interfaces
        for iface in existing_interfaces.values():
            iface.save()
            self.interface_disabled(context, iface)

        return context

    def process_interface(self, context, iface, data):
        """
        Performs per-interface processing.
        """

        # TODO: We currently assume that interfaces will not change types between wifi/non-wifi

        iface.hw_address = str(data.mac)
        iface.tx_packets = int(data.tx_packets)
        iface.rx_packets = int(data.rx_packets)
        iface.tx_bytes = int(data.tx_bytes)
        iface.rx_bytes = int(data.rx_bytes)
        iface.tx_errors = int(data.tx_errs)
        iface.rx_errors = int(data.rx_errs)
        iface.tx_drops = int(data.tx_drops)
        iface.rx_drops = int(data.rx_drops)
        iface.mtu = int(data.mtu)

        if iface.name in context.http.wireless.radios:
            data = context.http.wireless.radios[iface.name]

            # Wireless interface has some additional fields
            if data.mode == "ap":
                iface.mode = "ap"
            elif data.mode == "ibss":
                iface.mode = "mesh"
            elif data.mode == "managed":
                iface.mode = "sta"
            else:
                iface.mode = None
                self.logger.warning("Ignoring unknown wifi mode '%s' on node '%s'!" % (data.mode, node.pk))

            iface.essid = str(data.essid) if data.essid else None
            if data.bssid and iface.mode in ("mesh", "sta"):
                iface.bssid = str(data.bssid)
            else:
                iface.bssid = None

            iface.channel = int(data.channel) if data.channel else None
            iface.channel_width = int(data.channel_width) if data.channel_width else None
            iface.bitrate = float(data.bitrate) if data.bitrate else None
            iface.rts_threshold = int(data.rts_threshold) if data.rts_threshold else None
            iface.frag_threshold = int(data.frag_threshold) if data.frag_threshold else None
            iface.signal = int(data.signal) if data.signal else None
            iface.noise = int(data.noise) if data.noise else None
            # TODO: Calculate signal-to-noise ratio
            iface.snr = None

    def interface_enabled(self, context, iface):
        """
        Called when an interface has valid data (is available).
        """

        pass

    def interface_disabled(self, context, iface):
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

        def interface_enabled(self, context, iface):
            """
            Called when an interface has valid data (is available).
            """

            super(DatastreamInterfaces, self).interface_enabled(context, iface)
            self.set_interface_hidden(iface, False)

        def interface_disabled(self, context, iface):
            """
            Called when an interface is no longer available.
            """

            super(DatastreamInterfaces, self).interface_disabled(context, iface)
            self.set_interface_hidden(iface, True)
