from django import apps


class UnknownNodesConfig(apps.AppConfig):
    name = 'nodewatcher.modules.monitor.unknown_nodes'
    label = 'unknown_nodes'
