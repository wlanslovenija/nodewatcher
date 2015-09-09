from django import apps


class DatabaseEventSinkConfig(apps.AppConfig):
    name = 'nodewatcher.modules.events.sinks.db_sink'
    label = 'events_sinks_database'
