from nodewatcher.core.generator.cgm import base as cgm_base, devices as cgm_devices


class GenericX86NoWifi(cgm_devices.DeviceBase):
    """
    Generic x86 device descriptor.
    """

    identifier = 'generic-x86-nowifi'
    name = "x86 (no wireless)"
    manufacturer = "Generic"
    url = 'http://www.intel.com/'
    architecture = 'x86'
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
        'openwrt': {
            'eth0': 'eth0',
            'eth1': 'eth1',
            'eth2': 'eth2',
            'eth3': 'eth3',
        }
    }
    profiles = {
        'openwrt': {
            'name': 'Generic',
            'files': [
                'openwrt-x86-generic-rootfs-ext4.img.gz',
                'openwrt-x86-generic-vmlinuz'
            ]
        }
    }


class GenericX86HyperVNoWifi(GenericX86NoWifi):
    """
    Generic x86 Hyper-V device descriptor.
    """

    identifier = 'generic-x86hyperv-nowifi'
    name = "x86 Hyper-V (no wireless)"
    architecture = 'x86_hyperv'
    profiles = {
        'openwrt': {
            'name': 'Generic',
            'files': [
                'openwrt-x86-generic-combined-ext4.img.gz'
            ]
        }
    }


class GenericX86KVMNoWifi(GenericX86NoWifi):
    """
    Generic x86 KVM device descriptor.
    """

    identifier = 'generic-x86kvm-nowifi'
    name = "x86 KVM (no wireless)"
    architecture = 'x86_kvm'
    profiles = {
        'openwrt': {
            'name': 'Generic',
            'files': [
                'openwrt-x86-kvm_guest-combined-ext4.img.gz'
            ]
        }
    }


class GenericX86VMWareNoWifi(GenericX86NoWifi):
    """
    Generic x86 VMWare device descriptor.
    """

    identifier = 'generic-x86vmware-nowifi'
    name = "x86 VMWare (no wireless)"
    architecture = 'x86'
    profiles = {
        'openwrt': {
            'name': 'Generic',
            'files': [
                'openwrt-x86-generic-combined-ext4.vmdk'
            ]
        }
    }


class GenericX86VirtualBoxNoWifi(GenericX86NoWifi):
    """
    Generic x86 VirtualBox device descriptor.
    """

    identifier = 'generic-x86vbox-nowifi'
    name = "x86 VirtualBox (no wireless)"
    architecture = 'x86'
    profiles = {
        'openwrt': {
            'name': 'Generic',
            'files': [
                'openwrt-x86-generic-combined-ext4.vdi'
            ]
        }
    }


class GenericX86XENNoWifi(GenericX86NoWifi):
    """
    Generic x86 XEN device descriptor.
    """

    identifier = 'generic-x86xen-nowifi'
    name = "x86 XEN DomU (no wireless)"
    architecture = 'x86_xen'

# Register the Generic X86 devices.
cgm_base.register_device('openwrt', GenericX86NoWifi)
cgm_base.register_device('openwrt', GenericX86HyperVNoWifi)
cgm_base.register_device('openwrt', GenericX86KVMNoWifi)
cgm_base.register_device('openwrt', GenericX86VMWareNoWifi)
cgm_base.register_device('openwrt', GenericX86VirtualBoxNoWifi)
cgm_base.register_device('openwrt', GenericX86XENNoWifi)
