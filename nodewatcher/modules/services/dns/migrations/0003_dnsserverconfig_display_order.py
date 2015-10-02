# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services_dns', '0002_dnsserverconfig_annotations'),
    ]

    operations = [
        migrations.AddField(
            model_name='dnsserverconfig',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]
