# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0014_auto_20151025_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authenticationconfig',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='interfaceconfig',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='networkconfig',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='packageconfig',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
    ]
