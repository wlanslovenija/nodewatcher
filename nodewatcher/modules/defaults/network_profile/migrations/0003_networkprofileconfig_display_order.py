# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('defaults_network_profile', '0002_networkprofileconfig_annotations'),
    ]

    operations = [
        migrations.AddField(
            model_name='networkprofileconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]
