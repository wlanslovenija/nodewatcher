from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors


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

        version_ifaces = context.http.get_module_version("core.interfaces")
        version_wifi = context.http.get_module_version("core.wireless")
        if version_ifaces < 2 or version_wifi < 2:
            return context

        for name, data in context.http.iface.iteritems():
            try:
                iface = node.monitoring.core.interfaces(queryset=True).get(name=name).cast()
            except monitor_models.InterfaceMonitor.DoesNotExist:
                if name in context.http.wireless.radios:
                    iface = node.monitoring.core.interfaces(create=monitor_models.WifiInterfaceMonitor)
                else:
                    iface = node.monitoring.core.interfaces(create=monitor_models.InterfaceMonitor)
                iface.name = name

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

            if name in context.http.wireless.radios:
                data = context.http.wireless.radios[name]

                # Wireless interface has some additional fields
                if data.mode == "ap":
                    iface.mode = "ap"
                elif data.mode == "ibss":
                    iface.mode = "mesh"
                elif data.mode == "managed":
                    iface.mode = "sta"
                else:
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
                iface.snr = 0.0

            iface.save()

        return context
