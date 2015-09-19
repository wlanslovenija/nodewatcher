# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0002_auto_20150917_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobileinterfaceconfig',
            name='uplink',
            field=models.BooleanField(default=False),
        ),
    ]
