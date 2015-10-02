# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0002_statusmonitor_annotations'),
    ]

    operations = [
        migrations.AddField(
            model_name='statusmonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]
