# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields
import nodewatcher.core.validators
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0008_auto_20150922_0839'),
        ('vpn_tunneldigger', '0002_auto_20150921_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='tunneldiggerinterfaceconfig',
            name='uplink_interface',
            field=nodewatcher.core.registry.fields.ReferenceChoiceField(related_name='+', blank=True, to='cgm.InterfaceConfig', null=True),
        ),
        migrations.AlterField(
            model_name='tunneldiggerserver',
            name='ports',
            field=django.contrib.postgres.fields.ArrayField(models.IntegerField(validators=[nodewatcher.core.validators.PortNumberValidator()]), size=None),
        ),
    ]
