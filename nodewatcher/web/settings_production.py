# -*- coding: utf-8 -*-
#
# Production Django settings for wlan slovenija nodewatcher

from settings_wlansi import *

# Secrets are in a separate file so they are not visible in public repository
from secrets import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Jernej Kos', 'kostko@unimatrix-one.org'),
    ('Mitar', 'mitar.nodewatcher@tnode.com'),
)

MANAGERS = ADMINS

DATABASES = {
  'default' : {
    'ENGINE'   : 'django.db.backends.postgresql_psycopg2',
    'NAME'     : 'wlansi',
    'USER'     : 'wlansi_nw',
    'PASSWORD' : DB_PASSWORD, # Defined in secrets
    'HOST'     : 'dbpgsql',
    'PORT'     : '',
  }
}

EMAIL_TO_CONSOLE = False

EMAIL_HOST = 'mail'

SITEMAPS_USE_HTTPS = True
FEEDS_USE_HTTPS = True
USE_HTTPS = True

# We want that Django knows that it is in fact running behind a HTTPS-only proxy
MIDDLEWARE_CLASSES = (
  'web.nodes.middleware.HttpsMiddleware',
) + MIDDLEWARE_CLASSES

# SECRET_KEY is in secrets

# GOOGLE_MAPS_API_KEY is in secrets

MONITOR_WORKERS = 20
MONITOR_USER = 'nw-monitor'

DATA_ARCHIVE_ENABLED = True

IMAGE_GENERATOR_ENABLED = True
IMAGE_GENERATOR_SUSPENDED = False
IMAGE_GENERATOR_USER = 'nw-generator'

CACHE_BACKEND = "memcached://127.0.0.1:11211/"

ENABLE_GRAPH_DISPLAY = True
