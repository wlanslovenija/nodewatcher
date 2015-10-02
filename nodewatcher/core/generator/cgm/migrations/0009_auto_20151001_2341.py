# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0008_auto_20150922_0839'),
    ]

    operations = [
        migrations.AddField(
            model_name='authenticationconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='interfaceconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='interfacelimitconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='networkconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='packageconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]
