# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.extra.accounts.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofileandsettings',
            name='language',
            field=nodewatcher.extra.accounts.fields.LanguageField(default=nodewatcher.extra.accounts.fields.get_initial_language, help_text='Choose the language you wish this site to be in.', max_length=5, choices=[(b'en', 'English')]),
        ),
    ]
