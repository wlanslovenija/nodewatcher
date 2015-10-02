# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication_public_key', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='publickeyauthenticationconfig',
            options={'ordering': ['display_order', 'id']},
        ),
    ]
