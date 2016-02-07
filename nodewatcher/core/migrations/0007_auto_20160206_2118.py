# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20151018_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalconfig',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='node',
            name='registry_metadata',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='routeridconfig',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
    ]
