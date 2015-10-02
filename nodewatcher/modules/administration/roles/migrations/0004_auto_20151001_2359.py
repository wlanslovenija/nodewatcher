# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0003_roleconfig_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='roleconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='roleconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]
