# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('description', '0003_auto_20150926_0920'),
    ]

    operations = [
        migrations.AddField(
            model_name='descriptionconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]
