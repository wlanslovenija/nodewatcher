# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def move_to_qos(apps, schema_editor):
    InterfaceQoSConfig = apps.get_model('qos_base', 'InterfaceQoSConfig')
    ThroughputInterfaceLimitConfig = apps.get_model('cgm', 'ThroughputInterfaceLimitConfig')

    for old in ThroughputInterfaceLimitConfig.objects.all():
        new = InterfaceQoSConfig(
            root=old.root,
            interface=old.interface,
            enabled=old.enabled,
            download=int(old.limit_in or 0),
            upload=int(old.limit_out or 0),
        )
        new.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0012_wifiinterfaceconfig_isolate_clients'),
        ('qos_base', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(move_to_qos),
    ]
