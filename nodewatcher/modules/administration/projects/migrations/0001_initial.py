# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields
import django.contrib.gis.db.models.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True)),
                ('default_ip_pool', models.ForeignKey(related_name='+', verbose_name='Default IP pool', blank=True, to='core.IpPool', null=True)),
                ('ip_pools', models.ManyToManyField(related_name='projects', verbose_name='IP pools', to='core.IpPool', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_projects.projectconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('project', nodewatcher.core.registry.fields.ModelRegistryChoiceField(to='projects.Project', on_delete=django.db.models.deletion.PROTECT)),
                ('root', models.ForeignKey(related_name='config_projects_projectconfig', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SSID',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('purpose', models.CharField(max_length=50)),
                ('default', models.BooleanField(default=False)),
                ('bssid', nodewatcher.core.registry.fields.MACAddressField(max_length=17, null=True, verbose_name='BSSID', blank=True)),
                ('essid', models.CharField(max_length=50, verbose_name='ESSID')),
                ('project', models.ForeignKey(related_name='ssids', to='projects.Project')),
            ],
            options={
                'verbose_name': 'SSID',
            },
        ),
    ]
