from django import apps


class TunneldiggerVpnConfig(apps.AppConfig):
    name = 'nodewatcher.modules.vpn.tunneldigger'
    label = 'vpn_tunneldigger'
    verbose_name = "VPN: Tunneldigger"
