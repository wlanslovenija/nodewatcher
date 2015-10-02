# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_projectconfig_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='projectconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='projectconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]
