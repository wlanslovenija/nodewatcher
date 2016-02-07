# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields
import jsonfield


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0012_wifiinterfaceconfig_isolate_clients'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0006_auto_20151018_0956'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterfaceQoSConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_order', models.IntegerField(null=True, editable=False)),
                ('annotations', jsonfield.JSONField(default={}, help_text='Enter a valid JSON object', editable=False)),
                ('upload', models.PositiveIntegerField(default=0, help_text='Enter the upload speed in kbit/s, set to zero to disable upload limit.', verbose_name='Upload speed')),
                ('download', models.PositiveIntegerField(default=0, help_text='Enter the download speed in kbit/s, set to zero to disable download limit.', verbose_name='Download speed')),
                ('enabled', models.BooleanField(default=True)),
                ('interface', nodewatcher.core.registry.fields.IntraRegistryForeignKey(related_name='qos', editable=False, to='cgm.InterfaceConfig')),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_qos_base.interfaceqosconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='config_qos_base_interfaceqosconfig', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['display_order', 'id'],
                'abstract': False,
            },
        ),
    ]
