# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('types', '0002_typeconfig_annotations'),
    ]

    operations = [
        migrations.AddField(
            model_name='typeconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]
