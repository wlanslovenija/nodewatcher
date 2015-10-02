# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('routing_babel', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='babelroutingannouncemonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='babelroutingtopologymonitor',
            options={'ordering': ['display_order', 'id']},
        ),
    ]
