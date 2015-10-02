# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sensors_generic', '0003_auto_20150928_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='genericsensormonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]
