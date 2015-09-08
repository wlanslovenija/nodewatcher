# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DnsServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('address', nodewatcher.core.registry.fields.IPAddressField(host_required=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'DNS server',
            },
        ),
        migrations.CreateModel(
            name='DnsServerConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_services_dns.dnsserverconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='config_services_dns_dnsserverconfig', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PerProjectDnsServer',
            fields=[
                ('dnsserver_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='services_dns.DnsServer')),
                ('project', models.ForeignKey(related_name='+', to='projects.Project')),
            ],
            options={
                'verbose_name': 'Project-specific DNS server',
            },
            bases=('services_dns.dnsserver',),
        ),
        migrations.AddField(
            model_name='dnsserverconfig',
            name='server',
            field=nodewatcher.core.registry.fields.ModelRegistryChoiceField(to='services_dns.DnsServer', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='dnsserver',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_services_dns.dnsserver_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
