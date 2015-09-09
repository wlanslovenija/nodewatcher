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
            name='HttpTelemetrySourceConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.telemetry.http#source', default=b'poll', max_length=50, verbose_name='Telemetry Source', choices=[(b'poll', 'Periodic Poll'), (b'push', 'Push From Node')])),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_monitor_sources_http.httptelemetrysourceconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='config_monitor_sources_http_httptelemetrysourceconfig', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
