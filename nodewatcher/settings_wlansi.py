# -*- coding: utf-8 -*-
#
# Production Django settings for wlan slovenija nodewatcher.

from .settings import *

NETWORK_NAME = 'wlan slovenija'
NETWORK_HOME = 'http://wlan-si.net'
NETWORK_CONTACT = 'open@wlan-si.net'
NETWORK_CONTACT_PAGE = 'http://wlan-si.net/contact/'
NETWORK_DESCRIPTION = 'open wireless network of Slovenia'

EMAIL_SUBJECT_PREFIX = '[' + NETWORK_NAME + '] '
DEFAULT_FROM_EMAIL = 'open@wlan-si.net'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

EVENTS_EMAIL = 'events@wlan-si.net'
IMAGE_GENERATOR_EMAIL = 'generator@wlan-si.net'

# Add wlan slovenija specific things (templates, static files, etc.).
# We add to the beginning so that we can override templates in other apps.
INSTALLED_APPS = (
    'nodewatcher.extra.wlansi',
) + INSTALLED_APPS
