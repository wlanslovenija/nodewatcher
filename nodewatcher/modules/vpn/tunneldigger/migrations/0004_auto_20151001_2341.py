# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields
import nodewatcher.core.validators
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('vpn_tunneldigger', '0003_auto_20150930_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tunneldiggerinterfaceconfig',
            name='uplink_interface',
            field=nodewatcher.core.registry.fields.ReferenceChoiceField(related_name='+', blank=True, to='cgm.InterfaceConfig', help_text='Select this if you want to bind the tunnel only to a specific interface.', null=True),
        ),
        migrations.AlterField(
            model_name='tunneldiggerserver',
            name='ports',
            field=django.contrib.postgres.fields.ArrayField(models.IntegerField(validators=[nodewatcher.core.validators.PortNumberValidator()]), size=None),
        ),
    ]
