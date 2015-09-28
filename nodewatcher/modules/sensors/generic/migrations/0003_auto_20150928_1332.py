# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sensors_generic', '0002_genericsensormonitor_annotations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genericsensormonitor',
            name='value',
            field=models.FloatField(null=True),
        ),
    ]
