# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0013_move_qos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interfacelimitconfig',
            name='interface',
        ),
        migrations.RemoveField(
            model_name='interfacelimitconfig',
            name='polymorphic_ctype',
        ),
        migrations.RemoveField(
            model_name='interfacelimitconfig',
            name='root',
        ),
        migrations.RemoveField(
            model_name='throughputinterfacelimitconfig',
            name='interfacelimitconfig_ptr',
        ),
        migrations.DeleteModel(
            name='InterfaceLimitConfig',
        ),
        migrations.DeleteModel(
            name='ThroughputInterfaceLimitConfig',
        ),
    ]
