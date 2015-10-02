# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0003_locationconfig_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='locationconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='locationconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]
