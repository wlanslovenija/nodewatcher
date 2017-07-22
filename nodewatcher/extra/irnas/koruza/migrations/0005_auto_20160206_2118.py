# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('irnas_koruza', '0004_auto_20151205_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='koruzavpnmonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
    ]
