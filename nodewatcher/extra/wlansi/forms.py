from nodewatcher.core.registry import registration

from nodewatcher.core.generator.cgm.defaults import DefaultPlatform, DefaultRandomPassword, STAChannelAutoselect
from nodewatcher.modules.administration.types.defaults import DefaultType
from nodewatcher.modules.administration.projects.defaults import DefaultProject, DefaultProjectRouterID
from nodewatcher.modules.vpn.tunneldigger.defaults import TunneldiggerServersOnUplink
from nodewatcher.modules.services.dns.defaults import DnsServers

from .network import NetworkConfiguration


# Defaults for wlan slovenija network.
registration.point('node.config').add_form_defaults([
    DefaultPlatform(platform='lede'),
    DefaultType(type='wireless'),
    DefaultProject(),
    DefaultRandomPassword(),
    DefaultProjectRouterID(),
    NetworkConfiguration(routing_protocols=['babel']),
    STAChannelAutoselect(),
    TunneldiggerServersOnUplink(routing_protocols=['babel']),
    DnsServers(),
])
