# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor_sources_http', '0003_httptelemetrysourceconfig_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='httptelemetrysourceconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='httptelemetrysourceconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]
