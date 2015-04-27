from django.utils.translation import ugettext_lazy as _

# Import required for node.config registration point.
from nodewatcher.core import models as core_models
from nodewatcher.core.registry import registration, fields as registry_fields


class HttpTelemetrySourceConfig(registration.bases.NodeConfigRegistryItem):
    """
    HTTP telemetry source configuration.
    """

    source = registry_fields.RegistryChoiceField(
        'node.config', 'core.telemetry.http#source',
        default='poll',
        verbose_name=_("Telemetry Source"),
    )

    class RegistryMeta:
        form_weight = 5
        registry_id = 'core.telemetry.http'
        registry_section = _("Telemetry")
        registry_name = _("Basic Configuration")

registration.point('node.config').register_choice('core.telemetry.http#source', registration.Choice('poll', _("Periodic Poll")))
registration.point('node.config').register_choice('core.telemetry.http#source', registration.Choice('push', _("Push From Node")))
registration.point('node.config').register_item(HttpTelemetrySourceConfig)
