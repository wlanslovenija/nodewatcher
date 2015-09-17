# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0002_auto_20150917_1754'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommotionNetworkConfig',
            fields=[
                ('networkconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.NetworkConfig')),
                ('network_class', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'commotion.network#network_class', max_length=50, verbose_name='Class', choices=[(b'mesh', 'Mesh'), (b'client', 'Client'), (b'wired', 'Wired')])),
                ('dhcp', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'commotion.network#dhcp', default=b'auto', choices=[(b'auto', 'Auto'), (b'server', 'Server'), (b'client', 'Client')], max_length=50, blank=True, null=True, verbose_name='DHCP')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.networkconfig',),
        ),
    ]
