# coding=utf-8
# Development Django settings for your network nodewatcher.

import os.path
database_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db.sqlite').replace('\\', '/')
default_template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates').replace('\\', '/')
static_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static').replace('\\', '/')

import djcelery
djcelery.setup_loader()

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# A tuple that lists people who get code error notifications. When
# DEBUG=False and a view raises an exception, Django will e-mail these
# people with the full exception information. Each member of the tuple
# should be a tuple of (Full name, e-mail address).
ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
  'default' : {
    'ENGINE'   : 'django.contrib.gis.db.backends.postgis',
    'NAME'     : 'nodewatcher',
    'USER'     : 'nodewatcher',
    'PASSWORD' : '',
    'HOST'     : '',            # Set to empty string for localhost.
    'PORT'     : '',            # Set to empty string for default.
  },
}

# For local development it is better to send all e-mails to console
# Disable for production use and e-mails will be really send to users
# With version 1.2 Django supports e-mail backends which can be used instead of this
EMAIL_TO_CONSOLE = True

EMAIL_HOST = 'localhost'
EMAIL_SUBJECT_PREFIX = '[nodewatcher] '
EMAIL_EVENTS_SENDER = 'events@example.net'
EMAIL_IMAGE_GENERATOR_SENDER = 'generator@example.net'

NETWORK_NAME = 'your network name'
NETWORK_HOME = 'http://example.net'
NETWORK_CONTACT = 'open@example.net'
NETWORK_CONTACT_PAGE = 'http://example.net/contact'
NETWORK_DESCRIPTION = 'open wireless network in your neighborhood'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Ljubljana'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = static_dir

# URL that handles the media served from MEDIA_ROOT. Make sure to always
# use a trailing slash.
# Examples: "http://media.lawrence.com/", "http://example.net/media/"
MEDIA_URL = '/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Set to true if you want https instead of http in sitemaps' and feeds' URLs
SITEMAPS_USE_HTTPS = False
FEEDS_USE_HTTPS = False
# In general use https when constructing full URLs to nodewatcher?
USE_HTTPS = False

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1p)^zvjul0^c)v5*l!8^48g=ili!cn54^l)wl1avvu-x$==k7p'

# Google Maps API key for 127.0.0.1
GOOGLE_MAPS_API_KEY = 'ABQIAAAAsSAo-sxy6T5T7_DN1d9N4xRi_j0U6kJrkFvY4-OX2XYmEAa76BRH5tgaUAj1SaWR_RbmjkZ4zO7dDA'

# Where the map displaying all nodes is initially positioned
# Where the map is initially positioned when adding a new node is configured for each project in the database
GOOGLE_MAPS_DEFAULT_LAT = 46.05
GOOGLE_MAPS_DEFAULT_LONG = 14.507
GOOGLE_MAPS_DEFAULT_ZOOM = 13
GOOGLE_MAPS_DEFAULT_NODE_ZOOM = 15 # Zoom to use when displaying one node

# Configure with your bit.ly and Twitter user data to enable tweets via Twitther for some network events
#BITLY_LOGIN = "Your bit.ly login"
#BITLY_API_KEY = "Your bit.ly API key"
#TWITTER_USERNAME = "Your Twitter username"
#TWITTER_PASSWORD = "Your Twitter password"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.debug',
  'django.core.context_processors.i18n',
  'django.core.context_processors.media',
)

MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'web.urls'

TEMPLATE_DIRS = (
  # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
  default_template_dir,
)

DATE_FORMAT = 'Y-m-d H:i:s'
FORCE_SCRIPT_NAME = ''
LOGIN_REDIRECT_URL = '/my/nodes'
LOGIN_URL = '/auth/login'
RESET_PASSWORD_URL = 'http://example.net/reset_password'
PROFILE_CONFIGURATION_URL = 'http://example.net/prefs'
REGISTER_USER_URL = 'http://example.net/register'
AUTH_PROFILE_MODULE = 'account.useraccount'
ANONYMOUS_USER_ID = -1
# We are using SSO with Trac so we have our own auth module, you should probably use something from Django (also to register users)
# See http://docs.djangoproject.com/en/dev/topics/auth/
AUTHENTICATION_BACKENDS = (
  'web.account.auth.NodewatcherBackend',
  'guardian.backends.ObjectPermissionBackend',
)

INSTALLED_APPS = (
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.sitemaps',
  'django.contrib.gis',
  'djcelery',
  'web.nodes',
  'web.generator',
  'web.account',
  'web.dns',
  'web.policy',
  'web.monitor',
  'web.registry',
  'web.core',
  'web.core.cgm',
  'web.core.cgm.packages.solar',
  'web.core.cgm.packages.digitemp',
  'web.routing_olsr',
  'web.telemetry_http',
  'web.telemetry_core',
  'guardian',
  'south',
)

# Monitor configuration
MONITOR_WORKERS = 20 # Should be increased to much more (like 20) if your database can support simultaneous connections (SQLite does not)

# Cache backend
CACHE_BACKEND = "memcached://127.0.0.1:11211/"

# Celery
BROKER_BACKEND = "mongodb"
BROKER_HOST = "localhost"
BROKER_PORT = 27017
BROKER_VHOST = "nodewatcher"
CELERYD_PREFETCH_MULTIPLIER = 15
CELERY_IGNORE_RESULT = True

# Monitoring
MONITOR_PROCESSORS = (
  'web.routing_olsr.models.OLSRTopology',
  'web.routing_olsr.models.OLSRNodePostprocess',
  'web.telemetry_http.models.HTTPTelemetry',
  'web.telemetry_core.models.SystemStatusCheck',
  'web.monitor.processors.PurgeInvalidNodes'
)

OLSRD_MONITOR_HOST = '127.0.0.1'
OLSRD_MONITOR_PORT = 2006

# Registry
REGISTRY_RULES_MODULES = {
  'node.config' : 'web.rules'
}

DOCUMENTATION_LINKS = {
#  'custom_node'          : 'http://example.net/wiki/CustomNode',
#  'known_issues'         : 'http://example.net/wiki/KnownIssues',
#  'report_issue'         : 'http://example.net/newticket',
  'diversity'            : 'http://en.wikipedia.org/wiki/Antenna_diversity',
  'decimal_degrees'      : 'http://en.wikipedia.org/wiki/Decimal_degrees',
  'ip_address'           : 'http://en.wikipedia.org/wiki/IP_address',
#  'solar'                : 'http://example.net/wiki/Solar',
  'antenna_type'         : 'http://en.wikipedia.org/wiki/Antenna_%28radio%29',
  'antenna_polarization' : 'http://en.wikipedia.org/wiki/Antenna_%28radio%29#Polarization',
  'vpn'                  : 'http://en.wikipedia.org/wiki/Virtual_private_network',
  'snr'                  : 'http://en.wikipedia.org/wiki/Signal-to-noise_ratio',
  'bitrate'              : 'http://en.wikipedia.org/wiki/Bit_rate',
}

# Logging configuration
LOGGING = {
  'version': 1,
  'disable_existing_loggers': True,
  'formatters': {
    'verbose': {
      'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
    },
    'simple': {
      'format': '[%(levelname)s/%(name)s] %(message)s'
    },
  },
  'filters': {
  },
  'handlers': {
    'null': {
      'level':'DEBUG',
      'class':'django.utils.log.NullHandler',
    },
    'console':{
      'level':'DEBUG',
      'class':'logging.StreamHandler',
      'formatter': 'simple',
    },
    'mail_admins': {
      'level': 'ERROR',
      'class': 'django.utils.log.AdminEmailHandler',
    }
  },
  'loggers': {
    'django': {
      'handlers':['null'],
      'propagate': True,
      'level':'INFO',
    },
    'django.request': {
      'handlers': ['mail_admins'],
      'level': 'ERROR',
      'propagate': False,
    },
    'monitor': {
      'handlers': ['console'],
      'level': 'INFO',
    }
  }
}

