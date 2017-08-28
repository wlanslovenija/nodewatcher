# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20151018_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalconfig',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='node',
            name='registry_metadata',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='routeridconfig',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
    ]
