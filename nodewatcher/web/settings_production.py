# coding=utf-8
# Django production settings for nodewatcher project.

# Secrets are in a separate file so they are not visible in public repository
from secrets import *

# TODO Port to new style settings format

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Jernej Kos', 'kostko@unimatrix-one.org'),
)

MANAGERS = ADMINS

DATABASES = {
  'default' : {
    'ENGINE'   : 'django.db.backends.postgresql_psycopg2',
    'NAME'     : 'wlanlj',
    'USER'     : 'wlanlj',
    'PASSWORD' : DB_PASSWORD,
    'HOST'     : '',
    'PORT'     : '',
  }
}

EMAIL_HOST = 'mail.transwarp.si'
EMAIL_SUBJECT_PREFIX = '[wlan-lj] '
EMAIL_EVENTS_SENDER = 'events@wlan-lj.net'
EMAIL_IMAGE_GENERATOR_SENDER = 'generator@wlan-lj.net'

NETWORK_NAME = 'wlan ljubljana'
NETWORK_HOME = 'http://wlan-lj.net'
NETWORK_CONTACT = 'open@wlan-lj.net'
NETWORK_CONTACT_PAGE = 'http://wlan-lj.net/contact'
NETWORK_DESCRIPTION = 'odprto brezžično omrežje Ljubljane'

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
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# SECRET_KEY is in secrets

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.core.context_processors.auth',
  'django.core.context_processors.debug',
  'django.core.context_processors.i18n',
  'django.core.context_processors.media',
  'web.nodes.context_processors.web_client_node',
  'web.nodes.context_processors.global_values'
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
    '/var/www/django/wlanlj/templates',
    '/var/www/django/web/templates',
)

DATE_FORMAT = 'Y-m-d H:i:s'
FORCE_SCRIPT_NAME = ''
LOGIN_REDIRECT_URL = '/my/nodes'
LOGIN_URL = '/auth/login'
RESET_PASSWORD_URL = 'http://wlan-lj.net/reset_password'
PROFILE_CONFIGURATION_URL = 'http://wlan-lj.net/prefs'
AUTH_PROFILE_MODULE = 'account.useraccount'
AUTHENTICATION_BACKENDS = (
    'web.account.auth.CryptBackend',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'web.nodes',
    'web.generator',
    'web.account',
    'web.dns',
    'web.policy',
)

# Graph configuration
GRAPH_DIR = "/var/www/nodes.wlan-lj.net/graphs"
GRAPH_TIMESPANS = (
  ('day',   86400),
  ('week',  604800),
  ('month', 2678400),
  ('year',  33053184)
)

# Google maps
# GOOGLE_MAPS_API_KEY is in secrets
GOOGLE_MAPS_DEFAULT_LAT = 46.05
GOOGLE_MAPS_DEFAULT_LONG = 14.5
GOOGLE_MAPS_DEFAULT_ZOOM = 13
GOOGLE_MAPS_DEFAULT_NODE_ZOOM = 15

STATIC_DOC_ROOT = "/var/www/nodes.wlan-lj.net"

# Monitor configuration
MONITOR_WORKDIR = '/home/monitor'
MONITOR_WORKERS = 20
MONITOR_GRAPH_WORKERS = 5
MONITOR_POLL_INTERVAL = 240
MONITOR_OLSR_HOST = '127.0.0.1'
MONITOR_USER = 'monitor'
MONITOR_LOGFILE = '/var/log/wlanlj-monitor.log'

# Data archive configuration
DATA_ARCHIVE_ENABLED = True
DATA_ARCHIVE_HOST = '127.0.0.1'
DATA_ARCHIVE_PORT = 27017
DATA_ARCHIVE_DB = 'nodewatcher'

# Twitter configuration
BITLY_LOGIN = "wlanljubljana"
# BITLY_API_KEY is in secrets
TWITTER_USERNAME = "wlanljubljana"
# TWITTER_PASSWORD is in secrets

# Set to true if you want https instead of http in sitemaps' URLs 
SITEMAPS_USE_HTTPS = True
FEEDS_USE_HTTPS = True
USE_HTTPS = True

# Is generator enabled or not. If set to False the pybeanstalk dependency is not needed.
IMAGE_GENERATOR_ENABLED = True
IMAGE_GENERATOR_SUSPENDED = False
IMAGES_BINDIST_URL = 'http://bindist.wlan-lj.net/images/'

# Stickers
STICKERS_ENABLED = True
STICKERS_TEMP_DIR = '/tmp/'
STICKERS_DIR = '/var/www/nodes.wlan-lj.net/stickers'

# Are non-staff members allowed to mark a node as a border router
NONSTAFF_BORDER_ROUTERS = False

DOCUMENTATION_LINKS = {
  'custom_node'          : 'http://wlan-lj.net/wiki/Podrobnosti/PoMeri',
  'known_issues'         : 'http://wlan-lj.net/wiki/Podrobnosti/ZnaneTezave',
  'report_issue'         : 'http://wlan-lj.net/newticket',
  'diversity'            : 'http://wlan-lj.net/wiki/Diversity',
  'decimal_degrees'      : 'http://en.wikipedia.org/wiki/Decimal_degrees',
  'ip_address'           : 'http://wlan-lj.net/wiki/IPNaslov',
  'solar'                : 'http://wlan-lj.net/wiki/Podrobnosti/Solar',
  'antenna_type'         : 'http://wlan-lj.net/wiki/Antena',
  'antenna_polarization' : 'http://wlan-lj.net/wiki/Antena#Polarizacija',
  'vpn'                  : 'http://wlan-lj.net/wiki/VPN',
  'snr'                  : 'http://en.wikipedia.org/wiki/Signal-to-noise_ratio',
  'bitrate'              : 'http://en.wikipedia.org/wiki/Bit_rate',
}
