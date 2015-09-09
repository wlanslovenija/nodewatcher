# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.monitoring', b'core.status#network', max_length=50, null=True, choices=[(b'up', 'Up'), (b'down', 'Down'), (b'visible', 'Visible'), (None, 'Unknown')])),
                ('monitored', nodewatcher.core.registry.fields.NullBooleanChoiceField(b'node.monitoring', b'core.status#monitored')),
                ('health', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.monitoring', b'core.status#health', max_length=50, null=True, choices=[(b'healthy', 'Healthy'), (b'warnings', 'Warnings'), (b'errors', 'Errors'), (None, 'Unknown')])),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_status.statusmonitor_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='monitoring_status_statusmonitor', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
