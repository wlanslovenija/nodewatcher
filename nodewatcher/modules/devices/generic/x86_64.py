from nodewatcher.core.generator.cgm import base as cgm_base, devices as cgm_devices


class GenericX86_64NoWifi(cgm_devices.DeviceBase):
    """
    Generic x86-64 device descriptor.
    """

    identifier = 'generic-x86_64-nowifi'
    name = "x86_64 (no wireless)"
    manufacturer = "Generic"
    url = 'http://www.intel.com/'
    architecture = 'x86_64'
    radios = []
    switches = []
    ports = [
        cgm_devices.EthernetPort('eth0', "Eth0"),
        cgm_devices.EthernetPort('eth1', "Eth1"),
        cgm_devices.EthernetPort('eth2', "Eth2"),
        cgm_devices.EthernetPort('eth3', "Eth3"),
    ]
    antennas = []
    port_map = {
        'lede': {
            'eth0': 'eth0',
            'eth1': 'eth1',
            'eth2': 'eth2',
            'eth3': 'eth3',
        }
    }
    profiles = {
        'lede': {
            'name': 'Generic',
            'files': [
                '*-x86-64-combined-ext4.img.gz',
            ]
        }
    }


class GenericX86_64HyperVNoWifi(GenericX86_64NoWifi):
    """
    Generic x86 Hyper-V device descriptor.
    """

    identifier = 'generic-x86_64-hyperv-nowifi'
    name = "x86_64 Hyper-V (no wireless)"


class GenericX86_64KVMNoWifi(GenericX86_64NoWifi):
    """
    Generic x86 KVM device descriptor.
    """

    identifier = 'generic-x86_64-kvm-nowifi'
    name = "x86_64 KVM (no wireless)"


class GenericX86_64VMWareNoWifi(GenericX86_64NoWifi):
    """
    Generic x86 VMWare device descriptor.
    """

    identifier = 'generic-x86_64-vmware-nowifi'
    name = "x86_64 VMWare (no wireless)"
    profiles = {
        'lede': {
            'name': 'Generic',
            'files': [
                # Provide img.gz for sysupgrade support.
                '*-x86-64-combined-ext4.img.gz',
                '*-x86-64-combined-ext4.vmdk',
            ]
        }
    }


class GenericX86_64VirtualBoxNoWifi(GenericX86_64NoWifi):
    """
    Generic x86 VirtualBox device descriptor.
    """

    identifier = 'generic-x86_64-vbox-nowifi'
    name = "x86_64 VirtualBox (no wireless)"
    profiles = {
        'lede': {
            'name': 'Generic',
            'files': [
                # Provide img.gz for sysupgrade support.
                '*-x86-64-combined-ext4.img.gz',
                '*-x86-64-combined-ext4.vdi',
            ]
        }
    }

# Register the Generic x86-64 devices.
cgm_base.register_device('lede', GenericX86_64NoWifi)
cgm_base.register_device('lede', GenericX86_64HyperVNoWifi)
cgm_base.register_device('lede', GenericX86_64KVMNoWifi)
cgm_base.register_device('lede', GenericX86_64VMWareNoWifi)
cgm_base.register_device('lede', GenericX86_64VirtualBoxNoWifi)
