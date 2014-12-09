from django import apps


class VersionValidationConfig(apps.AppConfig):
    name = 'nodewatcher.modules.monitor.validation.version'
    label = 'validation_version'
