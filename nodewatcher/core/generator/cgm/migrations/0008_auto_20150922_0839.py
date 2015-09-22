# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0007_auto_20150921_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wifiinterfaceconfig',
            name='essid',
            field=models.CharField(max_length=50, null=True, verbose_name=b'ESSID'),
        ),
    ]
