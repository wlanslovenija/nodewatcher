# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qos_base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interfaceqosconfig',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
    ]
