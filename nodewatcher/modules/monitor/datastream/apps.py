from django import apps


class DatastreamConfig(apps.AppConfig):
    name = 'nodewatcher.modules.monitor.datastream'

    def ready(self):
        super(DatastreamConfig, self).ready()

        # Connect signals.
        from . import signals
