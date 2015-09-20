# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0005_auto_20150920_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='wifiinterfaceconfig',
            name='uplink',
            field=models.BooleanField(default=False),
        ),
    ]
