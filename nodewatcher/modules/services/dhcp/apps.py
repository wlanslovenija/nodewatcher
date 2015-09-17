from django import apps


class DhcpServiceConfig(apps.AppConfig):
    name = 'nodewatcher.modules.services.dhcp'
    label = 'services_dhcp'
    verbose_name = "DHCP"
