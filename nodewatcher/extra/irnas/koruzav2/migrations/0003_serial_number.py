# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-22 16:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('irnas_koruzav2', '0002_auto_20161013_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='koruzamonitor',
            name='serial_number',
            field=models.CharField(max_length=50, null=True),
        ),
    ]