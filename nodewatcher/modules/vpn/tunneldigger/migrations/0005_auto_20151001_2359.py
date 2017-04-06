# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.validators
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('vpn_tunneldigger', '0004_auto_20151001_2341'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tunneldiggerinterfaceconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='tunneldiggerserver',
            name='ports',
            field=django.contrib.postgres.fields.ArrayField(models.IntegerField(validators=[nodewatcher.core.validators.PortNumberValidator()]), size=None),
        ),
    ]
