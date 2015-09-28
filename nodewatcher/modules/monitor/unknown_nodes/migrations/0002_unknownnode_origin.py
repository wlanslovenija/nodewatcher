# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('unknown_nodes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='unknownnode',
            name='origin',
            field=models.CharField(default=b'unknown', max_length=20, choices=[(b'push', 'Push'), (b'unknown', 'Unknown')]),
        ),
    ]
