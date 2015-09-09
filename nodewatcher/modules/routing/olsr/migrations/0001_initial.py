# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
        ('cgm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkLocalAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', nodewatcher.core.registry.fields.IPAddressField(host_required=True, db_index=True)),
                ('interface', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OlsrdModTxtinfoPackageConfig',
            fields=[
                ('packageconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.PackageConfig')),
                ('port', models.IntegerField(default=2006)),
                ('allowed_host', nodewatcher.core.registry.fields.IPAddressField(default=b'127.0.0.1', help_text='IP of host that is allowed to connect to txtinfo feed.', host_required=True, verbose_name='Allowed host')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.packageconfig',),
        ),
        migrations.CreateModel(
            name='OlsrRoutingAnnounceMonitor',
            fields=[
                ('routingannouncemonitor_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='monitor.RoutingAnnounceMonitor')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('monitor.routingannouncemonitor',),
        ),
        migrations.CreateModel(
            name='OlsrRoutingTopologyMonitor',
            fields=[
                ('routingtopologymonitor_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='monitor.RoutingTopologyMonitor')),
                ('router_id', models.CharField(max_length=64, null=True)),
                ('average_lq', models.FloatField(null=True)),
                ('average_ilq', models.FloatField(null=True)),
                ('average_etx', models.FloatField(null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('monitor.routingtopologymonitor',),
        ),
        migrations.CreateModel(
            name='OlsrTopologyLink',
            fields=[
                ('topologylink_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='monitor.TopologyLink')),
                ('lq', models.FloatField(default=0.0)),
                ('ilq', models.FloatField(default=0.0)),
                ('etx', models.FloatField(default=0.0)),
            ],
            options={
                'abstract': False,
            },
            bases=('monitor.topologylink',),
        ),
        migrations.AddField(
            model_name='linklocaladdress',
            name='router',
            field=models.ForeignKey(related_name='link_local', to='routing_olsr.OlsrRoutingTopologyMonitor'),
        ),
    ]
