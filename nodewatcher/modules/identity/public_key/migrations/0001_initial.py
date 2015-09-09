# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('identity_base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicKeyIdentityConfig',
            fields=[
                ('identitymechanismconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='identity_base.IdentityMechanismConfig')),
                ('public_key', models.TextField()),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('identity_base.identitymechanismconfig',),
        ),
    ]
