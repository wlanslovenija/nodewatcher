# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0006_wifiinterfaceconfig_uplink'),
    ]

    operations = [
        migrations.AddField(
            model_name='authenticationconfig',
            name='annotations',
            field=models.TextField(default='{}', help_text='Enter a valid JSON object', editable=False),
        ),
        migrations.AddField(
            model_name='interfaceconfig',
            name='annotations',
            field=models.TextField(default='{}', help_text='Enter a valid JSON object', editable=False),
        ),
        migrations.AddField(
            model_name='interfacelimitconfig',
            name='annotations',
            field=models.TextField(default='{}', help_text='Enter a valid JSON object', editable=False),
        ),
        migrations.AddField(
            model_name='networkconfig',
            name='annotations',
            field=models.TextField(default='{}', help_text='Enter a valid JSON object', editable=False),
        ),
        migrations.AddField(
            model_name='packageconfig',
            name='annotations',
            field=models.TextField(default='{}', help_text='Enter a valid JSON object', editable=False),
        ),
    ]
