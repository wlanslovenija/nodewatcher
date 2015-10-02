# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20151001_2341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='routeridconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]
