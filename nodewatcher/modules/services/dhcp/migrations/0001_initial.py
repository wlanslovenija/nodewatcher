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
            name='DhcpLeaseConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mac_address', nodewatcher.core.registry.fields.MACAddressField(max_length=17, verbose_name='MAC Address')),
                ('ip_address', nodewatcher.core.registry.fields.IPAddressField(host_required=True, verbose_name='IP address')),
                ('hostname', models.CharField(max_length=50, null=True, blank=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_services_dhcp.dhcpleaseconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='config_services_dhcp_dhcpleaseconfig', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
