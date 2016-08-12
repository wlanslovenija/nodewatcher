from nodewatcher.core.monitor import models


def get_channel(node_bssid):
    """
    Gets the current channel of the BSSID

    :param node_bssid:
    :return:
    """

    return models.WifiInterfaceMonitor.objects.filter(bssid=node_bssid)[0].channel


def is_2ghz_bssid(node_bssid):
    """
    Is this BSSID associated to 2.4ghz or 5ghz?

    :param node_bssid:
    :return: Boolean whether the BSSID belongs to the 2.4ghz spectrum or not.
    """

    return models.WifiInterfaceMonitor.objects.filter(bssid=node_bssid)[0].channel <= 11


def get_available_channels(node_bssid):
    """
    Returns an array of available channels for that node.

    :param node_bssid: BSSID of a node
    :return: Array of available channels.
    """
    # TODO: Turn hard-coded array into a node-specific (stemming from regulatory practices) property.
    ch_2ghz = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    ch_5ghz = [36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 100, 102, 104, 106, 108, 110, 112, 114, 116,
               118, 120, 122, 124, 126, 128, 132, 134, 136, 138, 140, 142, 144, 149, 151, 153, 155, 157, 159, 161, 165]
    highest_2ghz_channel = max(ch_2ghz)

    if models.WifiInterfaceMonitor.objects.filter(bssid=node_bssid)[0].channel <= highest_2ghz_channel:
        return ch_2ghz
    else:
        return ch_5ghz
