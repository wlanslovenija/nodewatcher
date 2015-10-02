# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor_sources_http', '0002_httptelemetrysourceconfig_annotations'),
    ]

    operations = [
        migrations.AddField(
            model_name='httptelemetrysourceconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]
