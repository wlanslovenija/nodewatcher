# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0006_auto_20151018_0956'),
        ('irnas_koruza', '0002_auto_20151001_2359'),
    ]

    operations = [
        migrations.CreateModel(
            name='KoruzaVpnMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_order', models.IntegerField(null=True, editable=False)),
                ('annotations', models.TextField(default='{}', help_text='Enter a valid JSON object', editable=False)),
                ('ip_address', nodewatcher.core.registry.fields.IPAddressField(null=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_irnas_koruza.koruzavpnmonitor_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='monitoring_irnas_koruza_koruzavpnmonitor', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['display_order', 'id'],
                'abstract': False,
            },
        ),
    ]
