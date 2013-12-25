# -*- coding: utf-8 -*-
# pylint: skip-file
#
# Production Django settings for nodewatcher project.

from .settings_wlansi import *

# Secrets are in a separate file so they are not visible in public repository.
from .secrets import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Jernej Kos', 'kostko@unimatrix-one.org'),
    ('Mitar', 'mitar.nodewatcher@tnode.com'),
)

MANAGERS = ADMINS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# SECRET_KEY is in secrets.

# GOOGLE_MAPS_API_KEY is in secrets.

USE_HTTPS = True

CSRF_COOKIE_SECURE = USE_HTTPS
SESSION_COOKIE_SECURE = USE_HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTPS', 'on')

# We support some common password formats to ease transition.
AUTHENTICATION_BACKENDS += (
    'nodewatcher.extra.accounts.auth.AprBackend',
    'nodewatcher.extra.accounts.auth.CryptBackend',
)
