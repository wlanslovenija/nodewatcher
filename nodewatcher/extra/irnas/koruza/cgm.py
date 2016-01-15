from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base

from . import models


@cgm_base.register_platform_package('openwrt', 'netmeasured', models.KoruzaNetworkMeasurementConfig)
def koruza_network_measurement(node, pkgcfg, cfg):
    """
    Configures the KORUZA network measurement unit.
    """

    try:
        pkgcfg = pkgcfg.get()
    except models.KoruzaNetworkMeasurementConfig.MultipleObjectsReturned:
        raise cgm_base.ValidationError(_("Only one KORUZA network measurement unit may be defined."))

    # Ensure that the network measurement unit is a WDR4300.
    device = node.config.core.general().get_device()
    if not device or device.identifier != 'tp-wdr4300v1':
        raise cgm_base.ValidationError(_("Only TP-Link WDR4300v1 may be used as KORUZA network measurement unit."))

    # Reconfigure network, so that the first port of Lan0 is used for measurements.
    # XXX: This is currently hardcoded for TP-Link WDR4300 v1.
    # TODO: Port this to custom VLAN configuration when supported.
    vlan_lan0 = cfg.network.find_ordered_section('switch_vlan', vlan=1)
    if not vlan_lan0:
        raise cgm_base.ValidationError(_("Unable to find Lan0 port group to reconfigure for KORUZA network measurement unit."))
    vlan_lan0.ports = '0t 3 4 5'

    # Ensure that VLAN 3 is free.
    if cfg.network.find_ordered_section('switch_vlan', vlan=3) is not None:
        raise cgm_base.ValidationError(_("VLAN assignment conflicts with KORUZA network measurement unit."))

    vlan_measurement = cfg.network.add('switch_vlan')
    vlan_measurement.device = vlan_lan0.device
    vlan_measurement.vlan = 3
    vlan_measurement.ports = '0t 2'

    measurement_iface = cfg.network.add(interface='measure')
    measurement_iface.ifname = 'eth0.3'
    measurement_iface.proto = 'static'
    measurement_iface.netmask = '255.255.255.0'

    policy = cfg.network.add('rule')
    policy.dest = '172.16.88.0/24'
    policy.lookup = 'main'
    policy.priority = 500

    # Configure netmeasured.
    listener = cfg.netmeasured.add('listener')
    listener.interface = 'measure'
    listener.port = 9000

    probe = cfg.netmeasured.add(probe='koruza')
    probe.interface = 'measure'
    probe.port = 9000
    probe.interval = 100

    if pkgcfg.role == 'primary':
        measurement_iface.ipaddr = '172.16.88.1'
        listener.address = '172.16.88.1'
        probe.address = '172.16.88.2'
    elif pkgcfg.role == 'secondary':
        measurement_iface.ipaddr = '172.16.88.2'
        listener.address = '172.16.88.2'
        probe.address = '172.16.88.1'
    else:
        raise cgm_base.ValidationError(_("Unsupported KORUZA network measurement unit role '%s'.") % pkgcfg.role)

    # Install HTTP reporting scripts.
    cfg.files.install(
        '/www/cgi-bin/koruza/netmeasured_get',
        'irnas/koruza/netmeasured_get',
        mode=0755
    )

    cfg.files.install(
        '/www/cgi-bin/koruza/netmeasured_reset',
        'irnas/koruza/netmeasured_reset',
        mode=0755
    )

    # Configure webcam support if available.
    if cfg.has_package('mjpg-streamer'):
        streamer = cfg['mjpg-streamer'].add(**{'mjpg-streamer': 'core'})
        streamer.enabled = True
        streamer.input = 'uvc'
        streamer.output = 'http'
        streamer.device = '/dev/video0'
        streamer.resolution = '640x480'
        streamer.yuv = 0
        streamer.quality = 80
        streamer.fps = 5
        streamer.led = 'auto'
        streamer.www = '/www/webcam'
        streamer.port = 8080

        cfg.packages.add('mjpg-streamer')
