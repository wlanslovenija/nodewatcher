from nodewatcher.core.generator.cgm import base as cgm_base, devices as cgm_devices

from . import fon2100


class FoneraPlus(fon2100.Fonera):
    """
    Fonera FON-2200 device descriptor.
    """

    identifier = 'fon-2200'
    name = "Fonera+"
    switches = []
    ports = [
        cgm_devices.EthernetPort('wan0', "Wan0"),
        cgm_devices.EthernetPort('lan0', "Lan0"),
    ]
    port_map = {
        'openwrt': {
            'wifi0': 'wlan0',
            'sw0': 'eth0',
            'wan0': 'eth1',
            'lan0': 'eth0',
        }
    }

# Register the FON-2200 device
cgm_base.register_device('openwrt', FoneraPlus)
