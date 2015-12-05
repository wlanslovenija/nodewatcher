# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0014_auto_20151025_1357'),
        ('irnas_koruza', '0003_koruzavpnmonitor'),
    ]

    operations = [
        migrations.CreateModel(
            name='KoruzaNetworkMeasurementConfig',
            fields=[
                ('packageconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.PackageConfig')),
                ('role', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'irnas.koruza.netmeasure#role', default=b'primary', max_length=50, choices=[(b'primary', 'Primary'), (b'secondary', 'Secondary')])),
            ],
            options={
                'ordering': ['display_order', 'id'],
                'abstract': False,
            },
            bases=('cgm.packageconfig',),
        ),
        migrations.RemoveField(
            model_name='koruzaconfig',
            name='packageconfig_ptr',
        ),
        migrations.RemoveField(
            model_name='koruzaconfig',
            name='peer_controller',
        ),
        migrations.DeleteModel(
            name='KoruzaConfig',
        ),
    ]
