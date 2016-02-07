# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sensors_generic', '0005_auto_20151001_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genericsensormonitor',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
    ]
