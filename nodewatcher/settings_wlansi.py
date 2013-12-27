# -*- coding: utf-8 -*-
# pylint: skip-file
#
# Production Django settings for wlan slovenija nodewatcher.

from .settings import *

NETWORK.update({
    'NAME': 'wlan slovenija',
    'HOME': 'https://wlan-si.net',
    'CONTACT': 'open@wlan-si.net',
    'CONTACT_PAGE': 'http://wlan-si.net/contact/',
    'DESCRIPTION': 'open wireless network of Slovenia',
    'FAVICON_FILE': 'wlansi/images/favicon.ico',
    'LOGO_FILE': 'wlansi/images/logo.png',
    'DEFAULT_PROJECT': 'Test',
})

EMAIL_SUBJECT_PREFIX = '[' + NETWORK['NAME'] + '] '
DEFAULT_FROM_EMAIL = NETWORK['CONTACT']
SERVER_EMAIL = DEFAULT_FROM_EMAIL

EVENTS_EMAIL = 'events@wlan-si.net'
IMAGE_GENERATOR_EMAIL = 'generator@wlan-si.net'

# We add to the beginning so that we can override templates in other apps.
INSTALLED_APPS = (
    'nodewatcher.extra.wlansi',
) + INSTALLED_APPS
