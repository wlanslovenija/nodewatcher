# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-22 19:05
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0009_auto_20170405_1708'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='locationconfig',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='locationconfig',
            name='annotations',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, editable=False),
        ),
    ]
