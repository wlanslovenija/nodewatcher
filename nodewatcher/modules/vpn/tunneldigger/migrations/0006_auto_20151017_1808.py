# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import nodewatcher.core.validators
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0011_auto_20151007_2136'),
        ('vpn_tunneldigger', '0005_auto_20151001_2359'),
    ]

    operations = [
        migrations.CreateModel(
            name='TunneldiggerBrokerConfig',
            fields=[
                ('packageconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.PackageConfig')),
                ('routing_protocols', nodewatcher.core.registry.fields.RegistryMultipleChoiceField(blank=True, default=[], null=True, regpoint=b'node.config', enum_id=b'core.interfaces#routing_protocol', size=None)),
                ('ports', django.contrib.postgres.fields.ArrayField(models.IntegerField(validators=[nodewatcher.core.validators.PortNumberValidator()]), size=None)),
                ('max_cookies', models.PositiveIntegerField(default=1024)),
                ('max_tunnels', models.PositiveIntegerField(default=1024)),
                (b'tunnel_timeout', models.DurationField()),
                ('pmtu_discovery', models.BooleanField(default=True, verbose_name='Enable PMTU Discovery')),
                ('uplink_interface', nodewatcher.core.registry.fields.ReferenceChoiceField(related_name='+', blank=True, to='cgm.InterfaceConfig', help_text='Select on which interface the broker should listen on.', null=True)),
            ],
            options={
                'ordering': ['display_order', 'id'],
                'abstract': False,
            },
            bases=('cgm.packageconfig', models.Model),
        ),
        migrations.AlterField(
            model_name='tunneldiggerserver',
            name='ports',
            field=django.contrib.postgres.fields.ArrayField(models.IntegerField(validators=[nodewatcher.core.validators.PortNumberValidator()]), size=None),
        ),
    ]
