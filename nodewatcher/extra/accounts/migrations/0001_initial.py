# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_countries.fields
import nodewatcher.extra.accounts.fields
from django.conf import settings
import phonenumber_field.modelfields
import nodewatcher.modules.administration.projects.models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfileAndSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(help_text='Please enter your phone number in international format (e.g. +38651654321) for use in emergency. It will be visible only to network administrators.', max_length=128, null=True, verbose_name='phone number')),
                ('country', django_countries.fields.CountryField(blank=True, help_text='Where are you from? It will be public.', max_length=2)),
                ('language', nodewatcher.extra.accounts.fields.LanguageField(default=nodewatcher.extra.accounts.fields.get_initial_language, help_text='Choose the language you wish this site to be in.', max_length=5, choices=[(b'en', 'English'), (b'sl', 'Slovenian')])),
                ('attribution', models.CharField(default=b'name', help_text='What to use when we want to give you public attribution for your participation and contribution?', max_length=8, verbose_name='attribution', choices=[(b'name', 'Use my full name'), (b'username', 'Use my username'), (b'nothing', 'Hide me')])),
                ('default_project', models.ForeignKey(default=nodewatcher.modules.administration.projects.models.project_default, verbose_name='default project', to='projects.Project', null=True)),
                ('user', models.OneToOneField(related_name='profile', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user profile and settings',
                'verbose_name_plural': 'users profiles and settings',
            },
        ),
    ]
