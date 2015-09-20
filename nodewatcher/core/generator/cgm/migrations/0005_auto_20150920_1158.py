# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0004_auto_20150919_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobileinterfaceconfig',
            name='device',
            field=nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces#mobile_device', default=b'ppp0', max_length=50, choices=[(b'ppp0', 'PPP over USB0'), (b'qmi0', 'QMI over USB0')]),
        ),
    ]
