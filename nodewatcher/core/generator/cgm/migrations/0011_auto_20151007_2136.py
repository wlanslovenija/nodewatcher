# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0010_auto_20151001_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='wifiinterfaceconfig',
            name='bitrates',
            field=django.contrib.postgres.fields.ArrayField(default=[], null=True, base_field=models.CharField(max_length=50), size=None, blank=True),
        ),
        migrations.AddField(
            model_name='wifiinterfaceconfig',
            name='bitrates_preset',
            field=nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces#wifi_bitrates_preset', blank=True, max_length=50, null=True, choices=[(None, 'Allow all supported bitrates'), (b'exclude-80211b', 'Exclude legacy 802.11b bitrates'), (b'exclude-80211bg', 'Exclude legacy 802.11b/g bitrates'), (b'custom', 'Custom bitrate configuration')]),
        ),
    ]
