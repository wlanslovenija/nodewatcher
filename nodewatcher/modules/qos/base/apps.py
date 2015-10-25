from django import apps


class QoSBaseConfig(apps.AppConfig):
    name = 'nodewatcher.modules.qos.base'
    label = 'qos_base'
