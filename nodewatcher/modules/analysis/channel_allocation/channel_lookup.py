from nodewatcher.core.monitor import models


# TODO: Turn hard-coded arrays into a node-specific (stemming from regulatory practices) property.
ch_2ghz = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
ch_5ghz = [36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 100, 102, 104, 106, 108, 110, 112, 114, 116,
           118, 120, 122, 124, 126, 128, 132, 134, 136, 138, 140, 142, 144, 149, 151, 153, 155, 157, 159, 161, 165]
highest_2ghz_channel = max(ch_2ghz)

freq_list_2ghz_20mhz = [2412, 2417, 2422, 2427, 2432, 2437, 2442, 2447, 2452, 2457, 2462]
freq_list_2ghz_40mhz = [2412, 2417, 2422, 2427, 2432, 2437, 2442]
freq_list_2ghz_80mhz = []

freq_list_5ghz_20mhz = [5170, 5190, 5210, 5230, 5250, 5270, 5290, 5310, 5330, 5490, 5510, 5530, 5550, 5570, 5590,
                        5610, 5630, 5650, 5670, 5690, 5710, 5735, 5755, 5775, 5795, 5815]
freq_list_5ghz_40mhz = [5170, 5210, 5250, 5290, 5490, 5530, 5570, 5610, 5650, 5690, 5735, 5775]
freq_list_5ghz_80mhz = [5170, 5250, 5490, 5570, 5650, 5735]


def get_channel(node_bssid):
    """
    Returns the current channel of the BSSID.

    :param node_bssid: BSSID address on which we're performing the lookup.
    :return: Channel currently assigned to that network interface.
    """

    return models.WifiInterfaceMonitor.objects.filter(bssid=node_bssid)[0].channel


def is_2ghz_bssid(node_bssid):
    """
    Is this BSSID associated to 2.4ghz or 5ghz?

    :param node_bssid: BSSID address on which we're performing the lookup.
    :return: Boolean whether the BSSID belongs to the 2.4ghz spectrum or not.
    """

    return models.WifiInterfaceMonitor.objects.filter(bssid=node_bssid)[0].channel <= highest_2ghz_channel


def get_available_frequencies(node_bssid, channel_width):
    """
    Returns an array of available starting frequencies for that node.

    :param node_bssid: BSSID address on which we're performing the lookup.
    :return: Array of available channels.
    """

    if models.WifiInterfaceMonitor.objects.filter(bssid=node_bssid)[0].channel <= highest_2ghz_channel:
        if channel_width == 20:
            return freq_list_2ghz_20mhz
        elif channel_width == 40:
            return freq_list_2ghz_40mhz
        elif channel_width == 80:
            return freq_list_2ghz_80mhz
    else:
        if channel_width == 20:
            return freq_list_5ghz_20mhz
        elif channel_width == 40:
            return freq_list_5ghz_40mhz
        elif channel_width == 80:
            return freq_list_5ghz_80mhz
