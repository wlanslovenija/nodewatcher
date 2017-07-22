# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields
import django.db.models.deletion
import nodewatcher.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True, validators=[nodewatcher.core.validators.NodeNameValidator()])),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_core.generalconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IpPool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('family', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.network#ip_family', max_length=50, choices=[(b'ipv4', 'IPv4'), (b'ipv6', 'IPv6')])),
                ('network', models.CharField(max_length=50)),
                ('prefix_length', models.IntegerField()),
                ('status', models.IntegerField(default=0, editable=False)),
                ('description', models.CharField(max_length=200, null=True)),
                ('prefix_length_default', models.IntegerField(null=True, verbose_name='Default prefix length')),
                ('prefix_length_minimum', models.IntegerField(default=24, null=True, verbose_name='Minimum prefix length')),
                ('prefix_length_maximum', models.IntegerField(default=28, null=True, verbose_name='Maximum prefix length')),
                ('ip_subnet', nodewatcher.core.registry.fields.IPAddressField(null=True, editable=False)),
                ('held_from', models.DateTimeField(null=True, editable=False)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='core.IpPool', null=True)),
            ],
            options={
                'verbose_name': 'IP pool',
            },
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('uuid', models.CharField(max_length=40, serialize=False, primary_key=True)),
                ('registry_metadata', models.TextField(default='{}', help_text='Enter a valid JSON object', editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='RouterIdConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('router_id', models.CharField(max_length=100, editable=False)),
                ('rid_family', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.routerid#family', max_length=50, editable=False, choices=[(b'ipv4', 'IPv4'), (b'ipv6', 'IPv6')])),
            ],
        ),
        migrations.CreateModel(
            name='AllocatedIpRouterIdConfig',
            fields=[
                ('routeridconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.RouterIdConfig')),
                ('family', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.network#ip_family', max_length=50, choices=[(b'ipv4', 'IPv4'), (b'ipv6', 'IPv6')])),
                ('prefix_length', models.IntegerField(default=27)),
                ('subnet_hint', nodewatcher.core.registry.fields.IPAddressField(host_required=True, null=True, blank=True)),
                ('allocation', models.ForeignKey(related_name='allocations_core_allocatediprouteridconfig', on_delete=django.db.models.deletion.PROTECT, editable=False, to='core.IpPool', null=True)),
                ('pool', nodewatcher.core.registry.fields.ModelRegistryChoiceField(to='core.IpPool', on_delete=django.db.models.deletion.PROTECT)),
            ],
            bases=('core.routeridconfig', models.Model),
        ),
        migrations.CreateModel(
            name='StaticIpRouterIdConfig',
            fields=[
                ('routeridconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.RouterIdConfig')),
                ('address', nodewatcher.core.registry.fields.IPAddressField(subnet_required=True)),
            ],
            bases=('core.routeridconfig',),
        ),
        migrations.AddField(
            model_name='routeridconfig',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_core.routeridconfig_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='routeridconfig',
            name='root',
            field=models.ForeignKey(related_name='config_core_routeridconfig', editable=False, to='core.Node'),
        ),
        migrations.AddField(
            model_name='generalconfig',
            name='root',
            field=models.ForeignKey(related_name='config_core_generalconfig', editable=False, to='core.Node'),
        ),
    ]
