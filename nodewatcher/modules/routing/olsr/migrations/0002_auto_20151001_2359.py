# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('routing_olsr', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='olsrdmodtxtinfopackageconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='olsrroutingannouncemonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='olsrroutingtopologymonitor',
            options={'ordering': ['display_order', 'id']},
        ),
    ]
