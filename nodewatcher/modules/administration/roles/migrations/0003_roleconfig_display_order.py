# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0002_roleconfig_annotations'),
    ]

    operations = [
        migrations.AddField(
            model_name='roleconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]
