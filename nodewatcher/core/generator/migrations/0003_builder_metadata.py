# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0002_buildresultfile_hidden'),
    ]

    operations = [
        migrations.AddField(
            model_name='builder',
            name='metadata',
            field=models.TextField(default='{}', help_text='Enter a valid JSON object', editable=False, blank=True),
        ),
    ]
