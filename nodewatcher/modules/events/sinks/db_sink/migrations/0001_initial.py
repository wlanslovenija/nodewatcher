# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SerializedNodeEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('severity', models.IntegerField()),
                ('source_name', models.CharField(max_length=200)),
                ('source_type', models.CharField(max_length=200)),
                ('record', models.TextField(default='null', help_text='Enter a valid JSON object', null=True)),
                ('timestamp', models.DateTimeField()),
                ('related_nodes', models.ManyToManyField(related_name='events', to='core.Node')),
                ('related_users', models.ManyToManyField(related_name='events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SerializedNodeWarning',
            fields=[
                ('severity', models.IntegerField()),
                ('source_name', models.CharField(max_length=200)),
                ('source_type', models.CharField(max_length=200)),
                ('record', models.TextField(default='null', help_text='Enter a valid JSON object', null=True)),
                ('uuid', models.UUIDField(serialize=False, primary_key=True)),
                ('first_seen', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('related_nodes', models.ManyToManyField(related_name='warnings', to='core.Node')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
