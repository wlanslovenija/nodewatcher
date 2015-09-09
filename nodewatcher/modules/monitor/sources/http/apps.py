from django import apps


class HttpMonitorSourceConfig(apps.AppConfig):
    name = 'nodewatcher.modules.monitor.sources.http'
    label = 'monitor_sources_http'
