# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('description', '0002_descriptionconfig_annotations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='descriptionconfig',
            name='notes',
            field=models.TextField(default=b'', help_text='The notes field is private and is shown only to node maintainers.', blank=True),
        ),
    ]
