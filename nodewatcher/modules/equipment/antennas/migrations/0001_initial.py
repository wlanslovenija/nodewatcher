# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('cgm', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Antenna',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Manufacturer')),
                ('internal_for', models.CharField(max_length=100, null=True, editable=False)),
                ('internal_id', models.CharField(max_length=100, null=True, editable=False)),
                ('url', models.URLField(verbose_name='URL', blank=True)),
                ('polarization', models.CharField(max_length=20, choices=[(b'horizontal', 'Horizontal'), (b'vertical', 'Vertical'), (b'circular', 'Circular'), (b'dual', 'Dual')])),
                ('angle_horizontal', models.IntegerField(default=360, verbose_name='Horizontal angle')),
                ('angle_vertical', models.IntegerField(default=360, verbose_name='Vertical angle')),
                ('gain', models.IntegerField(verbose_name='Gain (dBi)')),
            ],
        ),
        migrations.CreateModel(
            name='AntennaEquipmentConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('azimuth', models.FloatField(null=True, blank=True)),
                ('elevation_angle', models.FloatField(null=True, blank=True)),
                ('rotation', models.FloatField(null=True, blank=True)),
                ('antenna', nodewatcher.core.registry.fields.ModelRegistryChoiceField(on_delete=django.db.models.deletion.PROTECT, blank=True, to='antennas.Antenna', null=True)),
                ('device', nodewatcher.core.registry.fields.IntraRegistryForeignKey(related_name='antennas', editable=False, to='cgm.WifiRadioDeviceConfig')),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_antennas.antennaequipmentconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='config_antennas_antennaequipmentconfig', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
