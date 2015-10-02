# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_projectconfig_annotations'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]
