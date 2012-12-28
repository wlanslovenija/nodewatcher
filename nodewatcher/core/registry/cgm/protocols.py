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

class WirelessProtocol(object):
    """
    Wireless protocol descriptor.
    """
    def __init__(self, identifier, description, channels, bitrates):
        """
        Class constructor.
        """
        self.identifier = identifier
        self.description = description
        self.channels = channels
        self.bitrates = bitrates

    def get_channel_choices(self, regulatory_filter = None):
        """
        Returns a list of channel chocies.
        """
        for channel in self.channels:
            if regulatory_filter is None or channel.frequency in regulatory_filter:
                yield channel.identifier, channel.number

    def get_channel(self, identifier):
        """
        Returns a specific channel descriptor.
        """
        for channel in self.channels:
            if channel.identifier == identifier:
                return channel

#
# IEEE 8022.11 B/G protocols
#
IEEE80211BG = WirelessProtocol(
  identifier = "ieee-80211bg",
  description = _("IEEE 802.11BG"),
  channels = [
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
  ],
  bitrates = [
    11,
    54
  ]
)

#
# IEEE 802.11 N protocol
#
IEEE80211N = WirelessProtocol(
  identifier = "ieee-80211n",
  description = _("IEEE 802.11N"),
  channels = [
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
  ],
  bitrates = [
    11,
    54
  ]
)
