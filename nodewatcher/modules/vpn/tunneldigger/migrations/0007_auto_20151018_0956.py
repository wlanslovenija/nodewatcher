# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import nodewatcher.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('vpn_tunneldigger', '0006_auto_20151017_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tunneldiggerbrokerconfig',
            name='ports',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(validators=[nodewatcher.core.validators.PortNumberValidator()]), size=None),
        ),
        migrations.AlterField(
            model_name='tunneldiggerserver',
            name='ports',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(validators=[nodewatcher.core.validators.PortNumberValidator()]), size=None),
        ),
    ]
