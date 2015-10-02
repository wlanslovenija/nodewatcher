# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('defaults_network_profile', '0003_networkprofileconfig_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='networkprofileconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='networkprofileconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]
