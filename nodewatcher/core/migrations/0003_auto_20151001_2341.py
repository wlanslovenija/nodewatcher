# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150921_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='routeridconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]
