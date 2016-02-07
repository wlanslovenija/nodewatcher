# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UnknownNode',
            fields=[
                ('uuid', models.CharField(max_length=40, serialize=False, primary_key=True)),
                ('first_seen', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('ip_address', models.GenericIPAddressField(null=True, unpack_ipv4=True)),
                ('certificate', jsonfield.JSONField(default='null', help_text='Enter a valid JSON object', null=True)),
            ],
        ),
    ]
