# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalAuthenticationKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Authentication key name.', max_length=100)),
                ('fingerprint', models.TextField(help_text='Public key fingerprint.', editable=False)),
                ('public_key', models.TextField(help_text='SSH encoded public key.')),
                ('created', models.DateTimeField(help_text='Timestamp when authentication key was first created.', auto_now_add=True)),
                ('enabled', models.BooleanField(default=True, help_text='Flag whether the authentication key should be enabled.')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PublicKeyAuthenticationConfig',
            fields=[
                ('authenticationconfig_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cgm.AuthenticationConfig')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('cgm.authenticationconfig',),
        ),
        migrations.CreateModel(
            name='UserAuthenticationKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Authentication key name.', max_length=100)),
                ('fingerprint', models.TextField(help_text='Public key fingerprint.', editable=False)),
                ('public_key', models.TextField(help_text='SSH encoded public key.')),
                ('created', models.DateTimeField(help_text='Timestamp when authentication key was first created.', auto_now_add=True)),
                ('user', models.ForeignKey(related_name='authentication_keys', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='publickeyauthenticationconfig',
            name='public_key',
            field=models.ForeignKey(to='authentication_public_key.UserAuthenticationKey'),
        ),
    ]
