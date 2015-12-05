from django import dispatch
from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base

from . import models, signals


@cgm_base.register_platform_module('openwrt', 15)
def qos_base(node, cfg):
    """
    Configures basic QoS rules (independent of interfaces).
    """

    def add_classify(target, ports, proto=None):
        c = cfg.qos.add('classify')
        c.target = target
        c.ports = ','.join([str(x) for x in ports])
        if proto is not None:
            c.proto = proto

    def add_default(target, proto=None, portrange=None, pktsize=None):
        d = cfg.qos.add('default')
        d.target = target
        if proto is not None:
            d.proto = proto
        if portrange is not None:
            d.portrange = '%d-%d' % portrange
        if pktsize is not None:
            d.pktsize = pktsize

    def add_reclassify(target, proto=None, pktsize=None, mark=None, tcpflags=None):
        r = cfg.qos.add('reclassify')
        r.target = target
        if proto is not None:
            r.proto = proto
        if pktsize is not None:
            r.pktsize = pktsize
        if mark is not None:
            r.mark = mark
        if tcpflags is not None:
            r.tcpflags = tcpflags

    def add_classgroup(name, classes, default):
        g = cfg.qos.add(classgroup=name)
        g.classes = ' '.join(classes)
        g.default = default

    def add_class(name, packetsize=None, packetdelay=None, maxsize=None, avgrate=None, priority=None):
        c = cfg.qos.add(**{'class': name})
        if packetsize is not None:
            c.packetsize = packetsize
        if packetdelay is not None:
            c.packetdelay = packetdelay
        if maxsize is not None:
            c.maxsize = maxsize
        if avgrate is not None:
            c.avgrate = avgrate
        if priority is not None:
            c.priority = priority

    # Configure default OpenWrt QoS rules.
    add_classify(target='Priority', ports=[22, 53])
    add_classify(target='Normal', proto='tcp', ports=[20, 21, 25, 80, 110, 443, 993, 995])
    add_classify(target='Express', ports=[5190])
    add_default(target='Express', proto='udp', pktsize=-500)
    add_reclassify(target='Priority', proto='icmp')
    add_default(target='Bulk', portrange=(1024, 65535))
    add_reclassify(target='Priority', proto='tcp', pktsize=-128, mark='!Bulk', tcpflags='SYN')
    add_reclassify(target='Priority', proto='tcp', pktsize=-128, mark='!Bulk', tcpflags='ACK')
    add_classgroup(name='Default', classes=['Priority', 'Express', 'Normal', 'Bulk'], default='Normal')
    add_class(name='Priority', packetsize=400, maxsize=400, avgrate=10, priority=20)
    add_class(name='Priority_down', packetsize=1000, avgrate=10)
    add_class(name='Express', packetsize=1000, maxsize=800, avgrate=50, priority=10)
    add_class(name='Normal', packetsize=1500, packetdelay=100, avgrate=10, priority=5)
    add_class(name='Normal_down', avgrate=20)
    add_class(name='Bulk', avgrate=1, packetdelay=200)

    # Ensure that we have qos-scripts installed.
    cfg.packages.add('qos-scripts')


def qos_apply_interface(cfg, interface):
    """
    Configures QoS on a single interface.
    """

    # Configure QoS for this interface when specified.
    for qos in interface.qos.filter(enabled=True):
        # Find the network section for the configured interface.
        network = cfg.network.find_named_section('interface', _managed_by=interface)
        if not network:
            raise cgm_base.ValidationError(
                _("Unable to find network configuration while configuring QoS for interface '%s'.") % interface
            )

        signals.cgm_apply_interface.send(
            qos.__class__,
            cfg=cfg,
            qos=qos,
            interface=interface,
            network=network,
        )

        break


def qos_apply_interfaces(cfg, interfaces, visited_interfaces):
    for interface in interfaces:
        if not interface.enabled or interface in visited_interfaces:
            continue

        visited_interfaces.add(interface)
        if interface.has_child_interfaces():
            qos_apply_interfaces(cfg, interface.get_child_interfaces(), visited_interfaces)
        else:
            qos_apply_interface(cfg, interface)


@cgm_base.register_platform_module('openwrt', 200)
def qos_interfaces(node, cfg):
    """
    Configures QoS on interfaces.
    """

    # Configure QoS on all interfaces.
    visited_interfaces = set()
    qos_apply_interfaces(cfg, node.config.core.interfaces(), visited_interfaces)


@dispatch.receiver(signals.cgm_apply_interface, sender=models.InterfaceQoSConfig, platform='openwrt')
def qos_interface_basic(sender, cfg, qos, interface, network, **kwargs):
    """
    Configures basic QoS for an interface.
    """

    policy = cfg.qos.add(interface=network.get_key())
    policy.enabled = True
    policy.classgroup = 'Default'

    if qos.download:
        policy.download = qos.download
    if qos.upload:
        policy.upload = qos.upload
