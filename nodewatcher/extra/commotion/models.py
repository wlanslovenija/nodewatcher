from nodewatcher.core.registry import registration

from nodewatcher.modules.monitor.sources.http import models as http_models

# Remove support for polling nodes as commotion only supports push.
registration.point('node.config').unregister_choice('core.telemetry.http#source', 'poll')
