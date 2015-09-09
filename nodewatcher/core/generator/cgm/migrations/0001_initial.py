# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields
import django.db.models.deletion
import timedelta.fields


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthenticationConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CgmGeneralConfig',
            fields=[
                ('generalconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.GeneralConfig')),
                ('platform', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.general#platform', max_length=50, blank=True)),
                ('router', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.general#router', max_length=50, blank=True)),
                ('build_channel', nodewatcher.core.registry.fields.ModelRegistryChoiceField(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='generator.BuildChannel', null=True)),
                ('version', nodewatcher.core.registry.fields.ModelRegistryChoiceField(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='generator.BuildVersion', null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('core.generalconfig',),
        ),
        migrations.CreateModel(
            name='InterfaceConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InterfaceLimitConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NetworkConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enabled', models.BooleanField(default=True)),
                ('description', models.CharField(max_length=100, blank=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PackageConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enabled', models.BooleanField(default=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_cgm.packageconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='config_cgm_packageconfig', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AllocatedNetworkConfig',
            fields=[
                ('networkconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.NetworkConfig')),
                ('family', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.network#ip_family', max_length=50, choices=[(b'ipv4', 'IPv4'), (b'ipv6', 'IPv6')])),
                ('prefix_length', models.IntegerField(default=27)),
                ('subnet_hint', nodewatcher.core.registry.fields.IPAddressField(host_required=True, null=True, blank=True)),
                ('routing_announces', nodewatcher.core.registry.fields.RegistryMultipleChoiceField(blank=True, default=[], regpoint=b'node.config', null=True, verbose_name='Announce Via', enum_id=b'core.interfaces.network#routing_announce', size=None)),
                ('lease_type', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.network#lease_type', blank=True, max_length=50, null=True, verbose_name='Lease Type', choices=[(b'dhcp', 'DHCP')])),
                (b'lease_duration', timedelta.fields.TimedeltaField(max_value=None, min_value=None)),
                ('nat_type', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.network#nat_type', blank=True, max_length=50, null=True, verbose_name='NAT Type', choices=[(b'snat-routed-networks', 'SNAT (towards routed networks)')])),
                ('allocation', models.ForeignKey(related_name='allocations_cgm_allocatednetworkconfig', on_delete=django.db.models.deletion.PROTECT, editable=False, to='core.IpPool', null=True)),
                ('pool', nodewatcher.core.registry.fields.ModelRegistryChoiceField(to='core.IpPool', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.networkconfig', models.Model),
        ),
        migrations.CreateModel(
            name='BridgedNetworkConfig',
            fields=[
                ('networkconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.NetworkConfig')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.networkconfig',),
        ),
        migrations.CreateModel(
            name='BridgeInterfaceConfig',
            fields=[
                ('interfaceconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.InterfaceConfig')),
                ('routing_protocols', nodewatcher.core.registry.fields.RegistryMultipleChoiceField(blank=True, default=[], null=True, regpoint=b'node.config', enum_id=b'core.interfaces#routing_protocol', size=None)),
                ('name', models.CharField(max_length=30)),
                ('stp', models.BooleanField(default=False, verbose_name='STP')),
                ('mac_address', nodewatcher.core.registry.fields.MACAddressField(max_length=17, null=True, verbose_name='Override MAC Address', blank=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.interfaceconfig', models.Model),
        ),
        migrations.CreateModel(
            name='DHCPNetworkConfig',
            fields=[
                ('networkconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.NetworkConfig')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.networkconfig',),
        ),
        migrations.CreateModel(
            name='EthernetInterfaceConfig',
            fields=[
                ('interfaceconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.InterfaceConfig')),
                ('routing_protocols', nodewatcher.core.registry.fields.RegistryMultipleChoiceField(blank=True, default=[], null=True, regpoint=b'node.config', enum_id=b'core.interfaces#routing_protocol', size=None)),
                ('eth_port', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces#eth_port', max_length=50)),
                ('uplink', models.BooleanField(default=False)),
                ('mac_address', nodewatcher.core.registry.fields.MACAddressField(max_length=17, null=True, verbose_name='Override MAC Address', blank=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.interfaceconfig', models.Model),
        ),
        migrations.CreateModel(
            name='MobileInterfaceConfig',
            fields=[
                ('interfaceconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.InterfaceConfig')),
                ('service', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces#mobile_service', default=b'umts', max_length=50, choices=[(b'umts', 'UMTS'), (b'gprs', 'GPRS'), (b'cdma', 'CDMA')])),
                ('device', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces#mobile_device', default=b'mobile0', max_length=50, choices=[(b'mobile0', 'Mobile0'), (b'mobile1', 'Mobile1')])),
                ('apn', models.CharField(max_length=100, verbose_name='APN')),
                ('pin', models.CharField(max_length=4, verbose_name='PIN')),
                ('username', models.CharField(max_length=50, blank=True)),
                ('password', models.CharField(max_length=50, blank=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.interfaceconfig',),
        ),
        migrations.CreateModel(
            name='PasswordAuthenticationConfig',
            fields=[
                ('authenticationconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.AuthenticationConfig')),
                ('password', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.authenticationconfig',),
        ),
        migrations.CreateModel(
            name='PPPoENetworkConfig',
            fields=[
                ('networkconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.NetworkConfig')),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.networkconfig',),
        ),
        migrations.CreateModel(
            name='StaticNetworkConfig',
            fields=[
                ('networkconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.NetworkConfig')),
                ('routing_announces', nodewatcher.core.registry.fields.RegistryMultipleChoiceField(blank=True, default=[], regpoint=b'node.config', null=True, verbose_name='Announce Via', enum_id=b'core.interfaces.network#routing_announce', size=None)),
                ('lease_type', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.network#lease_type', blank=True, max_length=50, null=True, verbose_name='Lease Type', choices=[(b'dhcp', 'DHCP')])),
                (b'lease_duration', timedelta.fields.TimedeltaField(max_value=None, min_value=None)),
                ('nat_type', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.network#nat_type', blank=True, max_length=50, null=True, verbose_name='NAT Type', choices=[(b'snat-routed-networks', 'SNAT (towards routed networks)')])),
                ('family', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.network#ip_family', max_length=50, choices=[(b'ipv4', 'IPv4'), (b'ipv6', 'IPv6')])),
                ('address', nodewatcher.core.registry.fields.IPAddressField(subnet_required=True)),
                ('gateway', nodewatcher.core.registry.fields.IPAddressField(host_required=True, null=True, blank=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.networkconfig', models.Model),
        ),
        migrations.CreateModel(
            name='ThroughputInterfaceLimitConfig',
            fields=[
                ('interfacelimitconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.InterfaceLimitConfig')),
                ('limit_out', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.limits#speeds', default=b'', max_length=50, verbose_name='Limit OUT', blank=True, choices=[(b'128', '128 Kbit/s'), (b'256', '256 Kbit/s'), (b'512', '512 Kbit/s'), (b'1024', '1 Mbit/s'), (b'2048', '2 Mbit/s'), (b'4096', '4 Mbit/s')])),
                ('limit_in', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.limits#speeds', default=b'', max_length=50, verbose_name='Limit IN', blank=True, choices=[(b'128', '128 Kbit/s'), (b'256', '256 Kbit/s'), (b'512', '512 Kbit/s'), (b'1024', '1 Mbit/s'), (b'2048', '2 Mbit/s'), (b'4096', '4 Mbit/s')])),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.interfacelimitconfig',),
        ),
        migrations.CreateModel(
            name='WifiInterfaceConfig',
            fields=[
                ('interfaceconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.InterfaceConfig')),
                ('routing_protocols', nodewatcher.core.registry.fields.RegistryMultipleChoiceField(blank=True, default=[], null=True, regpoint=b'node.config', enum_id=b'core.interfaces#routing_protocol', size=None)),
                ('mode', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces#wifi_mode', max_length=50, choices=[(b'mesh', 'Mesh'), (b'ap', 'AP'), (b'sta', 'STA')])),
                ('essid', models.CharField(max_length=50, verbose_name=b'ESSID')),
                ('bssid', nodewatcher.core.registry.fields.MACAddressField(max_length=17, null=True, verbose_name=b'BSSID', blank=True)),
                ('connect_to', models.ForeignKey(related_name='+', blank=True, to='core.Node', null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.interfaceconfig', models.Model),
        ),
        migrations.CreateModel(
            name='WifiRadioDeviceConfig',
            fields=[
                ('interfaceconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.InterfaceConfig')),
                ('wifi_radio', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces#wifi_radio', max_length=50)),
                ('protocol', models.CharField(max_length=50)),
                ('channel_width', models.CharField(max_length=50)),
                ('channel', models.CharField(max_length=50, null=True, blank=True)),
                ('antenna_connector', models.CharField(max_length=50, null=True)),
                ('tx_power', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('ack_distance', models.IntegerField(null=True, verbose_name='ACK Distance', blank=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.interfaceconfig',),
        ),
        migrations.AddField(
            model_name='networkconfig',
            name='interface',
            field=nodewatcher.core.registry.fields.IntraRegistryForeignKey(related_name='networks', editable=False, to='cgm.InterfaceConfig'),
        ),
        migrations.AddField(
            model_name='networkconfig',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_cgm.networkconfig_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='networkconfig',
            name='root',
            field=models.ForeignKey(related_name='config_cgm_networkconfig', editable=False, to='core.Node'),
        ),
        migrations.AddField(
            model_name='interfacelimitconfig',
            name='interface',
            field=nodewatcher.core.registry.fields.IntraRegistryForeignKey(related_name='limits', editable=False, to='cgm.InterfaceConfig'),
        ),
        migrations.AddField(
            model_name='interfacelimitconfig',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_cgm.interfacelimitconfig_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='interfacelimitconfig',
            name='root',
            field=models.ForeignKey(related_name='config_cgm_interfacelimitconfig', editable=False, to='core.Node'),
        ),
        migrations.AddField(
            model_name='interfaceconfig',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_cgm.interfaceconfig_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='interfaceconfig',
            name='root',
            field=models.ForeignKey(related_name='config_cgm_interfaceconfig', editable=False, to='core.Node'),
        ),
        migrations.AddField(
            model_name='authenticationconfig',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_cgm.authenticationconfig_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='authenticationconfig',
            name='root',
            field=models.ForeignKey(related_name='config_cgm_authenticationconfig', editable=False, to='core.Node'),
        ),
        migrations.AddField(
            model_name='wifiinterfaceconfig',
            name='device',
            field=nodewatcher.core.registry.fields.IntraRegistryForeignKey(related_name='interfaces', editable=False, to='cgm.WifiRadioDeviceConfig'),
        ),
        migrations.AddField(
            model_name='bridgednetworkconfig',
            name='bridge',
            field=nodewatcher.core.registry.fields.ReferenceChoiceField(related_name='bridge_ports', blank=True, to='cgm.BridgeInterfaceConfig', null=True),
        ),
    ]
