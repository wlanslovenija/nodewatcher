# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20151001_2341'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofileandsettings',
            name='id',
        ),
        migrations.AlterField(
            model_name='userprofileandsettings',
            name='user',
            field=models.OneToOneField(related_name='profile', primary_key=True, serialize=False, editable=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
