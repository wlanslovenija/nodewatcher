# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('antennas', '0003_antennaequipmentconfig_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='antennaequipmentconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='antennaequipmentconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]
