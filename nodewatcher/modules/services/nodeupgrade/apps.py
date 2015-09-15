from django import apps


class NodeupgradeServiceConfig(apps.AppConfig):
    name = 'nodewatcher.modules.services.nodeupgrade'
    label = 'services_nodeupgrade'
    verbose_name = "Nodeupgrade"
