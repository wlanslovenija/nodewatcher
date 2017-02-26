from nodewatcher.core.generator.cgm import base as cgm_base, devices as cgm_devices


class RaspberryPi1B(cgm_devices.DeviceBase):
    """
    Raspberry Pi v1 B device descriptor.
    """

    identifier = 'rpi-1b'
    name = "Raspberry Pi v1 (B)"
    manufacturer = "Raspberry Pi Foundation"
    url = 'https://www.raspberrypi.org/'
    architecture = 'brcm2708'
    radios = []
    switches = []
    usb = True
    ports = [
        cgm_devices.EthernetPort('eth0', "Eth0"),
    ]
    antennas = []
    port_map = {
        'openwrt': {
            'eth0': 'eth0',
        }
    }
    profiles = {
        'openwrt': {
            'name': 'RaspberryPi',
            'files': [
                '*-brcm2708-bcm2708-sdcard-vfat-ext4.img',
            ]
        }
    }


class RaspberryPi1BPlus(RaspberryPi1B):
    """
    Raspberry Pi v1 B+ device descriptor.
    """

    identifier = 'rpi-1bplus'
    name = "Raspberry Pi v1 (B+)"

# Register the Raspberry Pi devices.
cgm_base.register_device('openwrt', RaspberryPi1B)
cgm_base.register_device('openwrt', RaspberryPi1BPlus)
