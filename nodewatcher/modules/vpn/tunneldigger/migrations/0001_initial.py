# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields
import django.contrib.postgres.fields
import django.db.models.deletion
import nodewatcher.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('cgm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TunneldiggerInterfaceConfig',
            fields=[
                ('interfaceconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.InterfaceConfig')),
                ('routing_protocols', nodewatcher.core.registry.fields.RegistryMultipleChoiceField(blank=True, default=[], null=True, regpoint=b'node.config', enum_id=b'core.interfaces#routing_protocol', size=None)),
                ('mac', nodewatcher.core.registry.fields.MACAddressField(auto_add=True, max_length=17)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.interfaceconfig', models.Model),
        ),
        migrations.CreateModel(
            name='TunneldiggerServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('address', nodewatcher.core.registry.fields.IPAddressField(host_required=True)),
                ('ports', django.contrib.postgres.fields.ArrayField(models.IntegerField(validators=[nodewatcher.core.validators.PortNumberValidator()]), size=None)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Tunneldigger server',
            },
        ),
        migrations.CreateModel(
            name='PerProjectTunneldiggerServer',
            fields=[
                ('tunneldiggerserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='vpn_tunneldigger.TunneldiggerServer')),
                ('project', models.ForeignKey(related_name='+', to='projects.Project')),
            ],
            options={
                'verbose_name': 'Project-specific tunneldigger server',
            },
            bases=('vpn_tunneldigger.tunneldiggerserver',),
        ),
        migrations.AddField(
            model_name='tunneldiggerserver',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_vpn_tunneldigger.tunneldiggerserver_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='tunneldiggerinterfaceconfig',
            name='server',
            field=nodewatcher.core.registry.fields.ModelRegistryChoiceField(to='vpn_tunneldigger.TunneldiggerServer', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
