# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0003_builder_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='builder',
            name='metadata',
            field=models.TextField(editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='buildresult',
            name='config',
            field=models.TextField(help_text='Configuration used to build this firmware.', blank=True),
        ),
    ]
