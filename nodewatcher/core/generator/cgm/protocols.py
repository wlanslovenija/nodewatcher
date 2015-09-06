from django.utils.translation import ugettext as _


class Channel(object):
    """
    Channel descriptor.
    """

    def __init__(self, identifier, number, frequency):
        """
        Class constructor.
        """
        self.identifier = identifier
        self.number = number
        self.frequency = frequency


class ChannelWidth(object):
    """
    Channel width descriptor.
    """

    def __init__(self, identifier, description, width, limit_channels=None):
        """
        Class constructor.
        """
        self.identifier = identifier
        self.description = description
        self.width = width
        self.limit_channels = limit_channels


class Capability(object):
    """
    A wireless protocol capability.
    """

    def __init__(self, identifier):
        """
        Class constructor.
        """

        self.identifier = identifier


class WirelessProtocolMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_class = type.__new__(cls, name, bases, attrs)
        if cls == "WirelessProtocol":
            return new_class

        new_class.channels = ()
        new_class.widths = ()
        new_class.capabilities = set()
        new_class.available_capabilities = set()

        for base in bases:
            if not hasattr(base, 'identifier'):
                continue

            # Merge channels from base classes
            new_class.channels += base.channels
            # Merge channel widths from base classes
            new_class.widths += base.widths
            # Merge capabilities from base classes
            new_class.capabilities.update(base.capabilities)

        new_class.channels += attrs.get('channels', ())
        new_class.widths += attrs.get('widths', ())
        new_class.capabilities.update(attrs.get('capabilities', set()))

        for capability in new_class.capabilities:
            setattr(new_class, capability.identifier.replace('-', '_').upper(), capability)

        return new_class


class WirelessProtocol(object):
    """
    Wireless protocol descriptor.
    """

    __metaclass__ = WirelessProtocolMetaclass

    channels = ()
    widths = ()
    capabilities = ()
    available_capabilities = ()

    @classmethod
    def get_channel_choices(cls, width, regulatory_filter=None):
        """
        Returns a list of channel choices.
        """

        # No channels are available until channel width is known
        if width is None:
            return

        for channel in cls.channels:
            if (regulatory_filter is None or channel.frequency in regulatory_filter) and \
                    (width.limit_channels is None or width.limit_channels(cls, channel)):
                yield channel.identifier, "%d (%d MHz)" % (channel.number, channel.frequency)

    @classmethod
    def get_channel(cls, identifier):
        """
        Returns a specific channel descriptor.
        """

        for channel in cls.channels:
            if channel.identifier == identifier:
                return channel

    @classmethod
    def get_channel_number(cls, number):
        """
        Returns a specific channel descriptor.
        """

        for channel in cls.channels:
            if channel.number == number:
                return channel

    @classmethod
    def get_channel_width_choices(cls):
        """
        Returns a list of channel width choices.
        """

        for width in cls.widths:
            yield width.identifier, width.description

    @classmethod
    def get_channel_width(cls, identifier):
        """
        Returns a specific channel width descriptor.
        """

        for width in cls.widths:
            if width.identifier == identifier:
                return width

    def __init__(self, *capabilities):
        """
        Sets up available capabilities for this protocol.

        :param capabilities: A list of capabilities
        """

        capabilities = self.capabilities.intersection(capabilities)
        self.available_capabilities.update(capabilities)


class IEEE80211BG(WirelessProtocol):
    """
    IEEE 8022.11b/g protocols.
    """

    identifier = "ieee-80211bg"
    description = _("IEEE 802.11BG")
    channels = (
        Channel("ch1", 1, 2412),
        Channel("ch2", 2, 2417),
        Channel("ch3", 3, 2422),
        Channel("ch4", 4, 2427),
        Channel("ch5", 5, 2432),
        Channel("ch6", 6, 2437),
        Channel("ch7", 7, 2442),
        Channel("ch8", 8, 2447),
        Channel("ch9", 9, 2452),
        Channel("ch10", 10, 2457),
        Channel("ch11", 11, 2462),
        Channel("ch12", 12, 2467),
        Channel("ch13", 13, 2472),
    )
    widths = (
        ChannelWidth("nw5", _("5 MHz"), 5),
        ChannelWidth("nw10", _("10 MHz"), 10),
        ChannelWidth("ht20", _("20 MHz"), 20),
    )


class IEEE80211BGN(IEEE80211BG):
    """
    IEEE 802.11b/g + n protocol.
    """

    identifier = "ieee-80211bgn"
    description = _("IEEE 802.11BGN")
    capabilities = (
        Capability("LDPC"),
        Capability("GF"),
        Capability("SHORT-GI-20"),
        Capability("SHORT-GI-40"),
        Capability("TX-STBC"),
        Capability("TX-STBC1"),
        Capability("RX-STBC1"),
        Capability("RX-STBC12"),
        Capability("RX-STBC123"),
        Capability("DSSS_CCK-40"),
    )
    widths = (
        # Limit 40 MHz channels in 2.4 GHz band to sensible choices
        ChannelWidth(
            "ht40l",
            _("40 MHz (or 2x20 MHz, secondary is lower)"),
            40,
            limit_channels=lambda proto, channel: proto.get_channel_number(channel.number - 4) is not None,
        ),
        ChannelWidth(
            "ht40u",
            _("40 MHz (or 2x20 MHz, secondary is upper)"),
            40,
            limit_channels=lambda proto, channel: proto.get_channel_number(channel.number + 4) is not None,
        )
    )


class IEEE80211A(WirelessProtocol):
    """
    IEEE 802.11a protocol.
    """

    identifier = "ieee-80211a"
    description = _("IEEE 802.11A")
    channels = (
        Channel("ch36", 36, 5180),
        Channel("ch40", 40, 5200),
        Channel("ch44", 44, 5220),
        Channel("ch52", 52, 5240),
        Channel("ch56", 56, 5260),
        Channel("ch60", 60, 5280),
        Channel("ch64", 64, 5320),
        Channel("ch100", 100, 5500),
        Channel("ch104", 104, 5520),
        Channel("ch108", 108, 5540),
        Channel("ch112", 112, 5560),
        Channel("ch116", 116, 5580),
        Channel("ch120", 120, 5600),
        Channel("ch124", 124, 5620),
        Channel("ch128", 128, 5640),
        Channel("ch132", 132, 5660),
        Channel("ch136", 136, 5680),
        Channel("ch140", 140, 5700),
    )
    widths = (
        ChannelWidth("nw5", _("5 MHz"), 5),
        ChannelWidth("nw10", _("10 MHz"), 10),
        ChannelWidth("ht20", _("20 MHz"), 20),
    )


class IEEE80211AN(IEEE80211A):
    """
    IEEE 802.11a + n protocol.
    """

    identifier = "ieee-80211an"
    description = _("IEEE 802.11AN")
    capabilities = (
        Capability("LDPC"),
        Capability("GF"),
        Capability("SHORT-GI-20"),
        Capability("SHORT-GI-40"),
        Capability("TX-STBC"),
        Capability("TX-STBC1"),
        Capability("RX-STBC1"),
        Capability("RX-STBC12"),
        Capability("RX-STBC123"),
        Capability("DSSS_CCK-40"),
    )
    widths = (
        ChannelWidth(
            "ht40l",
            _("40 MHz (or 2x20 MHz, secondary is lower)"),
            40,
        ),
        ChannelWidth(
            "ht40u",
            _("40 MHz (or 2x20 MHz, secondary is upper)"),
            40,
        )
    )
