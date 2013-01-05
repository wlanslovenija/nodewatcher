# -*- coding: utf-8 -*-
#
# Development Django settings for nodewatcher project.

import os

settings_dir = os.path.abspath(os.path.dirname(__file__))

import djcelery
djcelery.setup_loader()

# Dummy function, so that "makemessages" can find strings which should be translated.
_ = lambda s: s

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
        # Follow https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/ to install GeoDjango.
        'ENGINE'   : 'django.contrib.gis.db.backends.postgis',
        'NAME'     : 'nodewatcher', # Use: createdb nodewatcher
        'USER'     : 'nodewatcher', # Set to empty string to connect as current user.
        'PASSWORD' : '',
        'HOST'     : 'localhost',   # Set to empty string for socket.
        'PORT'     : '',            # Set to empty string for default.
    },
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Ljubljana'

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

LANGUAGES = (
    ('en', _('English')),
)

LOCALE_PATHS = (
#   os.path.join(settings_dir, 'locale'),
)

URL_VALIDATOR_USER_AGENT = 'nodewatcher'

# Date input formats below take as first argument day and then month in x/y/z format.
DATE_INPUT_FORMATS = (
    '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', '%b %d %Y',
    '%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y',
    '%B %d, %Y', '%d %B %Y', '%d %B, %Y',
)

# All those formats are only defaults and are localized for users.
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

# We override defaults.
FORMAT_MODULE_PATH = 'nodewatcher.formats'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = os.path.join(settings_dir, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to always
# use a trailing slash.
# Examples: "http://media.lawrence.com/", "http://example.net/media/"
MEDIA_URL = '/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.abspath(os.path.join(settings_dir, '..', 'static'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# SCSS libraries to include in SCSSStaticFilesStorage.
SCSS_PATHS = [
    os.path.abspath(os.path.join(settings_dir, '..', 'libs', 'scss', 'compass')),
    os.path.abspath(os.path.join(settings_dir, '..', 'libs', 'scss', 'blueprint')),
]

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#   'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATICFILES_STORAGE = 'nodewatcher.core.frontend.staticfiles.storage.SCSSStaticFilesStorage'

GEOIP_PATH = os.path.abspath(os.path.join(settings_dir, '..', 'libs', 'geoip'))
DEFAULT_COUNTRY = 'SI'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1p)^zvjul0^c)v5*l!8^48g=ili!cn54^l)wl1avvu-x$==k7p'

EMAIL_HOST = 'localhost'
EMAIL_SUBJECT_PREFIX = '[nodewatcher] '
DEFAULT_FROM_EMAIL = 'webmaster@example.net'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#   'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'sekizai.context_processors.sekizai',
    'nodewatcher.core.frontend.context_processors.global_vars',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'nodewatcher.urls'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
#   os.path.join(settings_dir, 'templates'),
)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'

AUTH_PROFILE_MODULE = 'account.UserProfileAndSettings'

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN = True

# django-guardian anonymous user.
ANONYMOUS_USER_ID = -1

AUTHENTICATION_BACKENDS = (
    'nodewatcher.extra.account.auth.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

INSTALLED_APPS = (
    # We override staticfiles runserver with default Django runserver in nodewatcher.core.frontend.
    'django.contrib.staticfiles',

    # Ours are at the beginning so that we can override default templates in other apps.
    'nodewatcher.core',
    'nodewatcher.core.allocation',
    'nodewatcher.core.allocation.ip',
    'nodewatcher.core.frontend',
    'nodewatcher.core.generator.cgm',
    'nodewatcher.core.generator',
    'nodewatcher.core.monitor',
    'nodewatcher.core.monitor.sources.http',
    'nodewatcher.core.registry',
    'nodewatcher.modules.administration.types',
    'nodewatcher.modules.administration.projects',
    'nodewatcher.modules.administration.location',
    'nodewatcher.modules.administration.description',
    'nodewatcher.modules.administration.roles',
    'nodewatcher.modules.equipment',
    'nodewatcher.modules.equipment.antennas',
    'nodewatcher.modules.platforms.openwrt',
    'nodewatcher.modules.monitor.datastream',
    'nodewatcher.modules.monitor.http.resources',
    'nodewatcher.modules.routing.olsr',
    'nodewatcher.modules.sensors.digitemp',
    'nodewatcher.modules.sensors.solar',
    'nodewatcher.modules.vpn.tunneldigger',
    'nodewatcher.extra.account',

    # Legacy apps for migrations.
    'nodewatcher.legacy.nodes',
    'nodewatcher.legacy.policy',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'django.contrib.gis',

    'django_datastream',
    'djcelery',
    'guardian',
    'south',
    'sekizai',
    'missing',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '[%(levelname)s/%(name)s] %(message)s',
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
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'propagate': False,
        },
        # TODO: "monitor" or "nodewatcher.core.monitor"?
        'monitor': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'scss': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}

CELERY_RESULT_BACKEND = 'mongodb'
CELERY_MONGODB_BACKEND_SETTINGS = {
    'host': '127.0.0.1',
    'port': 27017,
    'database': 'nodewatcher',
    'taskmeta_collection': 'celery_taskmeta',
}

BROKER_URL = 'mongodb://127.0.0.1:27017/nodewatcher'

CELERY_ENABLE_UTC = USE_TZ
CELERY_TIMEZONE = TIME_ZONE
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERYD_PREFETCH_MULTIPLIER = 15
CELERY_IGNORE_RESULT = True

# Monitor configuration.
MONITOR_WORKERS = 20
MONITOR_INTERVAL = 300

# Monitoring processors configuration; this defines the order in which monitoring processors
# will be called. Multiple consecutive node processors will be automatically grouped and
# executed in parallel for all nodes that have been chosen so far by network processors. Only
# processors that are specified here will be called.
MONITOR_PROCESSORS = (
    'nodewatcher.modules.routing.olsr.processors.OLSRTopology',
    'nodewatcher.modules.routing.olsr.processors.OLSRNodePostprocess',
    'nodewatcher.core.monitor.sources.http.processors.HTTPTelemetry',
    'nodewatcher.modules.monitor.http.resources.processors.SystemStatus',
    'nodewatcher.modules.monitor.datastream.processors.Datastream',
    'nodewatcher.modules.administration.policy.processors.PurgeInvalidNodes'
)

# Backend for the monitoring data archive.
DATASTREAM_BACKEND = 'datastream.backends.mongodb.Backend'
# Each backend can have backend-specific settings that can be specified here.
DATASTREAM_BACKEND_SETTINGS = {
    'database_name': 'nodewatcher',
}

# Registry form processors hook into configuration changes
# performed by users via the forms user interface.
REGISTRY_FORM_PROCESSORS = {
    'node.config': (
        'nodewatcher.core.allocation.formprocessors.AutoPoolAllocator',
        'nodewatcher.core.generator.cgm.formprocessors.NodeCgmValidator',
    )
}

OLSRD_MONITOR_HOST = '127.0.0.1'
OLSRD_MONITOR_PORT = 2006

# Registry.
REGISTRY_RULES_MODULES = {
    'node.config': 'nodewatcher.rules',
}

# In general, use https when constructing full URLs to nodewatcher?
USE_HTTPS = False

# Google Maps API key for 127.0.0.1.
GOOGLE_MAPS_API_KEY = 'ABQIAAAAsSAo-sxy6T5T7_DN1d9N4xRi_j0U6kJrkFvY4-OX2XYmEAa76BRH5tgaUAj1SaWR_RbmjkZ4zO7dDA'

# Where the map displaying all nodes is initially positioned.
# Where the map is initially positioned when adding a new node is configured for each project in the database.
GOOGLE_MAPS_DEFAULT_LAT = 46.05
GOOGLE_MAPS_DEFAULT_LONG = 14.507
GOOGLE_MAPS_DEFAULT_ZOOM = 13
GOOGLE_MAPS_DEFAULT_NODE_ZOOM = 15 # Zoom to use when displaying one node.

NETWORK_NAME = 'your network name'
NETWORK_HOME = 'http://example.net'
NETWORK_CONTACT = 'open@example.net'
NETWORK_CONTACT_PAGE = 'http://example.net/contact'
NETWORK_DESCRIPTION = 'open wireless network in your neighborhood'

EVENTS_EMAIL = DEFAULT_FROM_EMAIL
IMAGE_GENERATOR_EMAIL = DEFAULT_FROM_EMAIL
