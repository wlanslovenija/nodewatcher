# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0003_mobileinterfaceconfig_uplink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobileinterfaceconfig',
            name='pin',
            field=models.CharField(max_length=4, verbose_name='PIN', blank=True),
        ),
    ]
