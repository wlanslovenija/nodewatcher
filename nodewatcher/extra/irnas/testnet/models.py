from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import registration

# Remove support for polling nodes.
registration.point('node.config').unregister_choice('core.telemetry.http#source', 'poll')

# Remove some default types. We keep backbone and wireless.
registration.point('node.config').unregister_choice('core.type#type', 'server')
registration.point('node.config').unregister_choice('core.type#type', 'test')
registration.point('node.config').unregister_choice('core.type#type', 'mobile')
registration.point('node.config').unregister_choice('core.type#type', 'dead')

# Register testnet-specific types.
registration.point('node.config').register_choice(
    'core.type#type',
    registration.Choice('gw', _("Gateway"), icon="node-type-server")
)
