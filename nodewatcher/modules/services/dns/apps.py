from django import apps


class DnsServiceConfig(apps.AppConfig):
    name = 'nodewatcher.modules.services.dns'
    label = 'services_dns'
    verbose_name = "DNS"
