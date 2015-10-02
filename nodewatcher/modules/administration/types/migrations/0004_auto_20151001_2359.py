# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('types', '0003_typeconfig_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='typeconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='typeconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]
