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
            name='AdjancencyHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('protocol', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces#routing_protocol', max_length=50, choices=[(b'olsr', 'OLSR'), (b'babel', 'Babel')])),
                ('first_seen', models.DateTimeField(auto_now_add=True)),
                ('node_a', models.ForeignKey(related_name='+', to='core.Node')),
                ('node_b', models.ForeignKey(related_name='+', to='core.Node')),
            ],
        ),
        migrations.CreateModel(
            name='ClientAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('family', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.monitoring', b'core.interfaces.network#family', max_length=50, null=True, choices=[(b'ipv4', 'IPv4'), (b'ipv6', 'IPv6')])),
                ('address', nodewatcher.core.registry.fields.IPAddressField()),
                ('expiry_time', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClientMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('client_id', models.CharField(max_length=32)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_monitor.clientmonitor_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='monitoring_monitor_clientmonitor', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GeneralMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_seen', models.DateTimeField(null=True)),
                ('last_seen', models.DateTimeField(null=True)),
                ('uuid', models.CharField(max_length=40, null=True)),
                ('firmware', models.CharField(max_length=100, null=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_monitor.generalmonitor_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='monitoring_monitor_generalmonitor', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GeneralResourcesMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('loadavg_1min', models.FloatField(null=True)),
                ('loadavg_5min', models.FloatField(null=True)),
                ('loadavg_15min', models.FloatField(null=True)),
                ('memory_free', models.PositiveIntegerField(null=True)),
                ('memory_buffers', models.PositiveIntegerField(null=True)),
                ('memory_cache', models.PositiveIntegerField(null=True)),
                ('memory_total', models.PositiveIntegerField(null=True)),
                ('processes', models.PositiveIntegerField(null=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_monitor.generalresourcesmonitor_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='monitoring_monitor_generalresourcesmonitor', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InterfaceMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True)),
                ('hw_address', nodewatcher.core.registry.fields.MACAddressField(max_length=17, null=True)),
                ('tx_packets', models.DecimalField(null=True, max_digits=100, decimal_places=0)),
                ('rx_packets', models.DecimalField(null=True, max_digits=100, decimal_places=0)),
                ('tx_bytes', models.DecimalField(null=True, max_digits=100, decimal_places=0)),
                ('rx_bytes', models.DecimalField(null=True, max_digits=100, decimal_places=0)),
                ('tx_errors', models.DecimalField(null=True, max_digits=100, decimal_places=0)),
                ('rx_errors', models.DecimalField(null=True, max_digits=100, decimal_places=0)),
                ('tx_drops', models.DecimalField(null=True, max_digits=100, decimal_places=0)),
                ('rx_drops', models.DecimalField(null=True, max_digits=100, decimal_places=0)),
                ('mtu', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NetworkAddressMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('family', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.monitoring', b'core.interfaces.network#family', max_length=50, null=True, choices=[(b'ipv4', 'IPv4'), (b'ipv6', 'IPv6')])),
                ('address', nodewatcher.core.registry.fields.IPAddressField(null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NetworkResourcesMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('routes', models.IntegerField(null=True)),
                ('tcp_connections', models.IntegerField(null=True)),
                ('udp_connections', models.IntegerField(null=True)),
                ('track_connections', models.IntegerField(null=True)),
                ('track_connections_max', models.IntegerField(null=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_monitor.networkresourcesmonitor_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='monitoring_monitor_networkresourcesmonitor', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RoutingAnnounceMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', nodewatcher.core.registry.fields.IPAddressField()),
                ('status', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.monitoring', b'network.routing.announces#status', max_length=50, null=True, choices=[(b'ok', 'OK'), (b'alias', 'Alias'), (b'unallocated', 'Unallocated'), (b'conflicting', 'Conflicting')])),
                ('last_seen', models.DateTimeField(null=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_monitor.routingannouncemonitor_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='monitoring_monitor_routingannouncemonitor', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RoutingTopologyMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('protocol', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces#routing_protocol', max_length=50, choices=[(b'olsr', 'OLSR'), (b'babel', 'Babel')])),
                ('link_count', models.IntegerField(default=0)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_monitor.routingtopologymonitor_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='monitoring_monitor_routingtopologymonitor', editable=False, to='core.Node')),
            ],
        ),
        migrations.CreateModel(
            name='RttMeasurementMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField(null=True)),
                ('end', models.DateTimeField(null=True)),
                ('packet_size', models.PositiveIntegerField(null=True)),
                ('packet_loss', models.PositiveIntegerField(null=True)),
                ('all_packets', models.PositiveIntegerField(null=True)),
                ('successful_packets', models.PositiveIntegerField(null=True)),
                ('failed_packets', models.PositiveIntegerField(null=True)),
                ('rtt_minimum', models.FloatField(null=True)),
                ('rtt_average', models.FloatField(null=True)),
                ('rtt_maximum', models.FloatField(null=True)),
                ('rtt_std', models.FloatField(null=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_monitor.rttmeasurementmonitor_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='monitoring_monitor_rttmeasurementmonitor', editable=False, to='core.Node')),
                ('source', models.ForeignKey(to='core.Node', null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SystemStatusMonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uptime', models.PositiveIntegerField(null=True)),
                ('local_time', models.DateTimeField(null=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_monitor.systemstatusmonitor_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='monitoring_monitor_systemstatusmonitor', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TopologyLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_seen', models.DateTimeField(null=True)),
                ('monitor', models.ForeignKey(related_name='links', to='monitor.RoutingTopologyMonitor')),
                ('peer', models.ForeignKey(related_name='links', to='core.Node')),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_monitor.topologylink_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WifiInterfaceMonitor',
            fields=[
                ('interfacemonitor_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='monitor.InterfaceMonitor')),
                ('mode', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces#wifi_mode', max_length=50, null=True, choices=[(b'mesh', 'Mesh'), (b'ap', 'AP'), (b'sta', 'STA')])),
                ('essid', models.CharField(max_length=50, null=True)),
                ('bssid', nodewatcher.core.registry.fields.MACAddressField(max_length=17, null=True)),
                ('protocol', models.CharField(max_length=50, null=True)),
                ('channel', models.PositiveIntegerField(null=True)),
                ('channel_width', models.PositiveIntegerField(null=True)),
                ('bitrate', models.FloatField(null=True)),
                ('rts_threshold', models.IntegerField(null=True)),
                ('frag_threshold', models.IntegerField(null=True)),
                ('signal', models.IntegerField(null=True)),
                ('noise', models.IntegerField(null=True)),
                ('snr', models.FloatField(null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('monitor.interfacemonitor',),
        ),
        migrations.AddField(
            model_name='networkaddressmonitor',
            name='interface',
            field=nodewatcher.core.registry.fields.IntraRegistryForeignKey(related_name='networks', to='monitor.InterfaceMonitor'),
        ),
        migrations.AddField(
            model_name='networkaddressmonitor',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_monitor.networkaddressmonitor_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='networkaddressmonitor',
            name='root',
            field=models.ForeignKey(related_name='monitoring_monitor_networkaddressmonitor', editable=False, to='core.Node'),
        ),
        migrations.AddField(
            model_name='interfacemonitor',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_monitor.interfacemonitor_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='interfacemonitor',
            name='root',
            field=models.ForeignKey(related_name='monitoring_monitor_interfacemonitor', editable=False, to='core.Node'),
        ),
        migrations.AddField(
            model_name='clientaddress',
            name='client',
            field=models.ForeignKey(related_name='addresses', to='monitor.ClientMonitor'),
        ),
        migrations.AlterUniqueTogether(
            name='routingtopologymonitor',
            unique_together=set([('root', 'protocol')]),
        ),
        migrations.AlterUniqueTogether(
            name='adjancencyhistory',
            unique_together=set([('node_a', 'node_b', 'protocol')]),
        ),
    ]
