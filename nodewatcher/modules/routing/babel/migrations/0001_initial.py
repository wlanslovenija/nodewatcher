# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BabelRoutingAnnounceMonitor',
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
            name='BabelRoutingTopologyMonitor',
            fields=[
                ('routingtopologymonitor_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='monitor.RoutingTopologyMonitor')),
                ('router_id', models.CharField(max_length=64, null=True)),
                ('average_rxcost', models.IntegerField(null=True)),
                ('average_txcost', models.IntegerField(null=True)),
                ('average_rttcost', models.IntegerField(null=True)),
                ('average_cost', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('monitor.routingtopologymonitor',),
        ),
        migrations.CreateModel(
            name='BabelTopologyLink',
            fields=[
                ('topologylink_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='monitor.TopologyLink')),
                ('interface', models.CharField(max_length=50, null=True)),
                ('rxcost', models.IntegerField(default=0)),
                ('txcost', models.IntegerField(default=0)),
                ('rtt', models.IntegerField(default=0, null=True)),
                ('rttcost', models.IntegerField(default=0, null=True)),
                ('cost', models.IntegerField(default=0)),
                ('reachability', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=('monitor.topologylink',),
        ),
        migrations.CreateModel(
            name='LinkLocalAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', nodewatcher.core.registry.fields.IPAddressField(host_required=True, db_index=True)),
                ('interface', models.CharField(max_length=50, null=True)),
                ('router', models.ForeignKey(related_name='link_local', to='routing_babel.BabelRoutingTopologyMonitor')),
            ],
        ),
    ]
