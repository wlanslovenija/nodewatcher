from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import registration, fields as registry_fields
from nodewatcher.core.generator.cgm import models as cgm_models

from nodewatcher.modules.monitor.sources.http import models as http_models

# Remove support for polling nodes as commotion only supports push.
registration.point('node.config').unregister_choice('core.telemetry.http#source', 'poll')


class CommotionNetworkConfig(cgm_models.NetworkConfig):
    network_class = registry_fields.RegistryChoiceField(
        'node.config', 'commotion.network#network_class',
        verbose_name=_("Class"),
    )

    dhcp = registry_fields.RegistryChoiceField(
        'node.config', 'commotion.network#dhcp',
        verbose_name=_("DHCP"),
        null=True, blank=True,
    )

    class RegistryMeta(cgm_models.NetworkConfig.RegistryMeta):
        registry_name = _("Commotion")

registration.point('node.config').register_choice('commotion.network#network_class', registration.Choice('mesh', _("Mesh")))
registration.point('node.config').register_choice('commotion.network#network_class', registration.Choice('client', _("Client")))
registration.point('node.config').register_choice('commotion.network#network_class', registration.Choice('wired', _("Wired")))
registration.point('node.config').register_choice('commotion.network#dhcp', registration.Choice('auto', _("Auto")))
registration.point('node.config').register_choice('commotion.network#dhcp', registration.Choice('server', _("Server")))
registration.point('node.config').register_choice('commotion.network#dhcp', registration.Choice('client', _("Client")))
registration.point('node.config').register_subitem(cgm_models.EthernetInterfaceConfig, CommotionNetworkConfig)
registration.point('node.config').register_subitem(cgm_models.WifiInterfaceConfig, CommotionNetworkConfig)
registration.point('node.config').register_subitem(cgm_models.BridgeInterfaceConfig, CommotionNetworkConfig)
