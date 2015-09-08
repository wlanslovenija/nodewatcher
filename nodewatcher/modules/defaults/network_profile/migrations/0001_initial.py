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
            name='NetworkProfileConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profiles', nodewatcher.core.registry.fields.RegistryMultipleChoiceField(help_text='Selected network profiles affect how the node is configured when automatic defaults are enabled. In case defaults are disabled, selecting network profiles will have no effect.', blank=True, default=[], null=True, regpoint=b'node.config', enum_id=b'network.profile#profiles', size=None)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_defaults_network_profile.networkprofileconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='config_defaults_network_profile_networkprofileconfig', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
