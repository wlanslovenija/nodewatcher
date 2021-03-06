# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-05 11:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('identity_base', '0006_auto_20161013_1344'),
    ]

    operations = [
        migrations.CreateModel(
            name='HmacIdentityConfig',
            fields=[
                ('identitymechanismconfig_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='identity_base.IdentityMechanismConfig')),
                ('key', models.TextField()),
            ],
            options={
                'ordering': ['display_order', 'id'],
                'abstract': False,
            },
            bases=('identity_base.identitymechanismconfig',),
        ),
    ]
