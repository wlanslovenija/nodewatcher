# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0003_statusmonitor_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statusmonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='statusmonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]
