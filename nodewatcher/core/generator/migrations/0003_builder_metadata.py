# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0002_buildresultfile_hidden'),
    ]

    operations = [
        migrations.AddField(
            model_name='builder',
            name='metadata',
            field=json_field.fields.JSONField(default='null', help_text='Enter a valid JSON object', editable=False, blank=True),
        ),
    ]
