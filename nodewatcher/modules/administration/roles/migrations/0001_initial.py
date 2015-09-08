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
            name='RoleConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('roles', nodewatcher.core.registry.fields.RegistryMultipleChoiceField(blank=True, default=[], null=True, regpoint=b'node.config', enum_id=b'core.roles#roles', size=None)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_roles.roleconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='config_roles_roleconfig', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
