# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0011_auto_20151007_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='wifiinterfaceconfig',
            name='isolate_clients',
            field=models.BooleanField(default=True, help_text='Enable to isolate clients connected to the same AP from each other.'),
        ),
    ]
