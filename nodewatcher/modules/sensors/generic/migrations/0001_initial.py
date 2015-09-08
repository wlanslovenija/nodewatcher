# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericSensorMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sensor_id', models.CharField(max_length=100)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('unit', models.CharField(max_length=50)),
                ('value', models.FloatField()),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_sensors_generic.genericsensormonitor_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='monitoring_sensors_generic_genericsensormonitor', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
