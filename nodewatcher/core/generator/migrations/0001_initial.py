# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.generator.models
from django.conf import settings
import jsonfield
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildChannel',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False, help_text='A unique build channel identifier.')),
                ('name', models.CharField(help_text='Human-readable build channel name.', unique=True, max_length=20)),
                ('description', models.TextField(help_text='Optional build channel description.', blank=True)),
                ('created', models.DateTimeField(help_text='Timestamp when build channel was first registered.', auto_now_add=True)),
                ('last_modified', models.DateTimeField(help_text='Timestamp when build channel was last modified.', auto_now=True)),
                ('default', models.BooleanField(default=False, help_text='Use this build channel as default.')),
            ],
        ),
        migrations.CreateModel(
            name='Builder',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False, help_text='A unique builder identifier.')),
                ('platform', models.CharField(help_text='Platform identifier.', max_length=50, editable=False, blank=True)),
                ('architecture', models.CharField(help_text='Architecture identifier.', max_length=50, editable=False, blank=True)),
                ('host', models.CharField(help_text='Builder host, reachable over SSH and HTTP.', max_length=50)),
                ('private_key', models.TextField(help_text='Private key for SSH authentication.')),
            ],
        ),
        migrations.CreateModel(
            name='BuildResult',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False, help_text='A unique build result identifier.')),
                ('config', jsonfield.JSONField(default={}, help_text='Configuration used to build this firmware.', blank=True)),
                ('build_log', models.TextField(help_text='Last lines of the build log.', null=True, blank=True)),
                ('created', models.DateTimeField(help_text='Timestamp when build result was created.', auto_now_add=True)),
                ('last_modified', models.DateTimeField(help_text='Timestamp when build result was last modified.', auto_now=True)),
                ('status', models.CharField(default=b'pending', help_text='Build status.', max_length=15, choices=[(b'pending', 'pending'), (b'building', 'building'), (b'failed', 'failed'), (b'ok', 'ok')])),
                ('build_channel', models.ForeignKey(help_text='Firmware build channel used.', to='generator.BuildChannel')),
                ('builder', models.ForeignKey(help_text='Firmware builder host used.', to='generator.Builder')),
                ('node', models.ForeignKey(help_text='Node this firmware build is for.', to='core.Node')),
                ('user', models.ForeignKey(help_text='User that requested this firmware build.', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BuildResultFile',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False, help_text='A unique build result file identifier.')),
                ('file', models.FileField(max_length=200, upload_to=nodewatcher.core.generator.models.generate_build_result_filename)),
                ('checksum_md5', models.CharField(max_length=32)),
                ('checksum_sha256', models.CharField(max_length=64)),
                ('result', models.ForeignKey(related_name='files', to='generator.BuildResult')),
            ],
        ),
        migrations.CreateModel(
            name='BuildVersion',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False, help_text='A unique build version identifier.')),
                ('created', models.DateTimeField(help_text='Timestamp when firmware version was first registered.', auto_now_add=True)),
                ('name', models.CharField(help_text='Build version name.', unique=True, max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='builder',
            name='version',
            field=models.ForeignKey(related_name='builders', blank=True, editable=False, to='generator.BuildVersion'),
        ),
        migrations.AddField(
            model_name='buildchannel',
            name='builders',
            field=models.ManyToManyField(help_text='Builders that can build this version.', related_name='channels', to='generator.Builder', blank=True),
        ),
    ]
