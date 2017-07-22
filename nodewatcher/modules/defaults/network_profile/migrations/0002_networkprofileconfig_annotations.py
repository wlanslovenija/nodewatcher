# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('defaults_network_profile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='networkprofileconfig',
            name='annotations',
            field=models.TextField(default='{}', help_text='Enter a valid JSON object', editable=False),
        ),
    ]
