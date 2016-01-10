# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0004_auto_20151001_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='interfacemonitor',
            name='up',
            field=models.BooleanField(default=False),
        ),
    ]
