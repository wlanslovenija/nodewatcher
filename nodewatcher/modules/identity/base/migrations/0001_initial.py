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
            name='IdentityConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trust_policy', nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.identity#trust_policy', default=b'first', max_length=50, choices=[(b'any', 'Trust any identity (INSECURE)'), (b'first', 'Trust and store the first received identity'), (b'config', 'Only trust explicitly configured identities')])),
                ('store_unknown', models.BooleanField(default=True, help_text='Set in order for unknown identities to be stored, so you may later confirm them. Until they are confirmed, they are not trusted.', verbose_name='Store Unknown Identities')),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_identity_base.identityconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='config_identity_base_identityconfig', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IdentityMechanismConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trusted', models.BooleanField(default=False)),
                ('automatically_added', models.BooleanField(default=False, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(null=True, editable=False, blank=True)),
                ('identity', nodewatcher.core.registry.fields.IntraRegistryForeignKey(related_name='mechanisms', editable=False, to='identity_base.IdentityConfig')),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_identity_base.identitymechanismconfig_set+', editable=False, to='contenttypes.ContentType', null=True)),
                ('root', models.ForeignKey(related_name='config_identity_base_identitymechanismconfig', editable=False, to='core.Node')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
