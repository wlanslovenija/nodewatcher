from django import apps


class WatchdogServiceConfig(apps.AppConfig):
    name = 'nodewatcher.modules.services.watchdog'
    label = 'services_watchdog'
    verbose_name = "Watchdog"
