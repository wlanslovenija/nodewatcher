from django import apps


class InterfaceValidationConfig(apps.AppConfig):
    name = 'nodewatcher.modules.monitor.validation.interfaces'
    label = 'validation_interfaces'
