# coding=utf-8
# Development Django settings for your network nodewatcher.

import os.path
settings_dir = os.path.abspath(os.path.dirname(__file__))
database_file = os.path.join(settings_dir, 'db.sqlite')
default_template_dir = os.path.join(settings_dir, 'templates')
locale_dir = os.path.join(settings_dir, 'locale')
geoip_dir = os.path.abspath(os.path.join(settings_dir, '..', 'geoip'))
static_dir = os.path.abspath(os.path.join(settings_dir, '..', 'static'))

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
    'NAME'     : 'nodewatcher', # createdb nodewatcher
    'USER'     : '',            # Set to empty string to connect as current user.
    'PASSWORD' : '',
    'HOST'     : 'localhost',   # Set to empty string for localhost.
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

_ = lambda s: s # Dummy function so that makemessages finds it
LANGUAGES = (
  ('en', _('English')),
)

LOCALE_PATHS = (
  locale_dir,
)

GEOIP_PATH = geoip_dir
DEFAULT_COUNTRY = 'SI'

URL_VALIDATOR_USER_AGENT = 'Django'

# Date input formats below take as first argument day and then month in x/y/z format
DATE_INPUT_FORMATS = (
  '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', '%b %d %Y',
  '%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y',
  '%B %d, %Y', '%d %B %Y', '%d %B, %Y',
)

# All those formats are only defaults and are localized for users
DATE_FORMAT = 'd/M/Y'
TIME_FORMAT = 'H:i'
DATETIME_FORMAT = 'd/M/Y, H:i:s'
YEAR_MONTH_FORMAT = 'F Y'
MONTH_DAY_FORMAT = 'j F'
SHORT_DATE_FORMAT = 'd/m/y'
SHORT_DATETIME_FORMAT = 'd/m/y H:i'
FIRST_DAY_OF_WEEK = 1
DECIMAL_SEPARATOR = '.'
THOUSAND_SEPARATOR = ','
NUMBER_GROUPING = 0

# We override defaults
FORMAT_MODULE_PATH = 'nodewatcher.formats'

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
  'django.contrib.messages.context_processors.messages',
  'nodewatcher.nodes.context_processors.global_values',
)

MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'nodewatcher.urls'

TEMPLATE_DIRS = (
  # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
  default_template_dir,
)

FORCE_SCRIPT_NAME = ''

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'

AUTH_PROFILE_MODULE = 'account.UserProfileAndSettings'

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN = True

ANONYMOUS_USER_ID = -1

AUTHENTICATION_BACKENDS = (
  'nodewatcher.account.auth.ModelBackend',
  'nodewatcher.account.auth.AprBackend',
  'nodewatcher.account.auth.CryptBackend',
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
  'django_datastream',
  'nodewatcher.nodes',
  'nodewatcher.generator',
  'nodewatcher.account',
  'nodewatcher.policy',

  'nodewatcher.registry',
  'nodewatcher.registry.loader',
  'nodewatcher.core',
  'nodewatcher.core.cgm',
  'nodewatcher.core.cgm.packages.solar',
  'nodewatcher.core.cgm.packages.digitemp',
  'nodewatcher.monitor',
  'nodewatcher.datastream',
  'nodewatcher.routing_olsr',
  'nodewatcher.telemetry_http',
  'nodewatcher.telemetry_core',
  'nodewatcher.firmware_core',
  'nodewatcher.firmware_tunneldigger',
  'guardian',
  'south',
)

# Monitor configuration
MONITOR_WORKERS = 20
MONITOR_INTERVAL = 300

# Cache backend
CACHE_BACKEND = "memcached://127.0.0.1:11211/"

# Celery
BROKER_URL = "mongodb://localhost/nodewatcher"
CELERYD_PREFETCH_MULTIPLIER = 15
CELERY_IGNORE_RESULT = True

import datetime
CELERYBEAT_SCHEDULE = {
  # Datastream downsampler needs to run every minute to check if any downsampling
  # needs to be performed
  "datastream_downsampler" : {
    "task" : "nodewatcher.datastream.tasks.run_downsampling",
    "schedule" : datetime.timedelta(minutes = 1),
  }
}

# Monitoring processors configuration; this defines the order in which monitoring processors
# will be called. Multiple consecutive node processors will be automatically grouped and
# executed in parallel for all nodes that have been chosen so far by network processors. Only
# processors that are specified here will be called.
MONITOR_PROCESSORS = (
  'nodewatcher.routing_olsr.processors.OLSRTopology',
  'nodewatcher.routing_olsr.processors.OLSRNodePostprocess',
  'nodewatcher.telemetry_http.processors.HTTPTelemetry',
  'nodewatcher.telemetry_core.processors.SystemStatusCheck',
  'nodewatcher.datastream.processors.DataStreamProcessor',
  'nodewatcher.monitor.processors.PurgeInvalidNodes'
)

# Backend for the monitoring data archive
DATASTREAM_BACKEND = 'datastream.backends.mongodb.Backend'
# Each backend can have backend-specific settings that can be specified here
DATASTREAM_BACKEND_SETTINGS = {
  'database_name': 'nodewatcher',
}

# Registry form processors hook into configuration changes
# performed by users via the forms user interface
REGISTRY_FORM_PROCESSORS = {
  'node.config': (
    'nodewatcher.core.allocation.processors.AutoPoolAllocator',
    'nodewatcher.core.cgm.processors.NodeCgmValidator',
  )
}

# Configuration generating modules for firmware images
CGM_MODULES = (
  'nodewatcher.core.cgm.openwrt',
  'nodewatcher.firmware_core.openwrt',
  'nodewatcher.firmware_tunneldigger.openwrt',
  'nodewatcher.routing_olsr.cgm',
)

OLSRD_MONITOR_HOST = '127.0.0.1'
OLSRD_MONITOR_PORT = 2006

# Registry
REGISTRY_RULES_MODULES = {
  'node.config': 'nodewatcher.rules',
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
