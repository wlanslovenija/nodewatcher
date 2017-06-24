from nodewatcher.core.registry import forms as registry_forms

from .ethernet import EthernetModule
from .mobile import MobileUplinkModule
from .wireless import WirelessModule


class NetworkConfiguration(registry_forms.ComplexFormDefaults):
    modules = [
        EthernetModule(),
        MobileUplinkModule(),
        WirelessModule(),
    ]

    def __init__(self, routing_protocols):
        super(NetworkConfiguration, self).__init__(
            routing_protocols=routing_protocols,
        )
