# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.validators
import postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('vpn_tunneldigger', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tunneldiggerserver',
            name='ports',
            field=postgres.fields.ArrayField(models.IntegerField(validators=[nodewatcher.core.validators.PortNumberValidator()]), size=None),
        ),
    ]
