from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import registration

# Remove support for polling nodes as KORUZA only supports push.
registration.point('node.config').unregister_choice('core.telemetry.http#source', 'poll')

# Remove default types.
registration.point('node.config').unregister_choice('core.type#type', 'server')
registration.point('node.config').unregister_choice('core.type#type', 'backbone')
registration.point('node.config').unregister_choice('core.type#type', 'wireless')
registration.point('node.config').unregister_choice('core.type#type', 'test')
registration.point('node.config').unregister_choice('core.type#type', 'mobile')
registration.point('node.config').unregister_choice('core.type#type', 'dead')

# Register KORUZA-specific types.
registration.point('node.config').register_choice('core.type#type', registration.Choice('koruza', _("KORUZA"), icon="node-type-wireless"))
registration.point('node.config').register_choice('core.type#type', registration.Choice('test', _("Test Device"), icon="node-type-test"))
registration.point('node.config').register_choice('core.type#type', registration.Choice('sensor', _("Sensor"), icon="node-type-mobile"))
