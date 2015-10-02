# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('description', '0004_descriptionconfig_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='descriptionconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='descriptionconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]
