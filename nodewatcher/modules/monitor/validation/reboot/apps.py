from django import apps


class RebootValidationConfig(apps.AppConfig):
    name = 'nodewatcher.modules.monitor.validation.reboot'
    label = 'validation_reboot'
