# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='KoruzaConfig',
            fields=[
                ('packageconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.PackageConfig')),
                ('serial_port', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'irnas.koruza#serial_port', default=b'usb0', max_length=50, choices=[(b'usb0', 'USB0'), (b'usb1', 'USB1')])),
                ('peer_controller', models.ForeignKey(related_name='+', blank=True, to='core.Node', null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.packageconfig',),
        ),
    ]
