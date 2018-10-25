from django import apps


class SNMPConfig(apps.AppConfig):
    name = 'nodewatcher.modules.monitor.sources.snmp'
    label = 'snmp'
    verbose_name = "SNMP Daemon"
