from django import apps


class TopologyConfig(apps.AppConfig):
    name = 'nodewatcher.modules.monitor.topology'
    label = 'monitor_topology'
