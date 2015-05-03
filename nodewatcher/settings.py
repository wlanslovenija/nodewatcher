# -*- coding: utf-8 -*-
# pylint: skip-file
#
# Development Django settings for nodewatcher project.

import os

settings_dir = os.path.abspath(os.path.dirname(__file__))

# Dummy function, so that "makemessages" can find strings which should be translated.
_ = lambda s: s

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEMPLATE_URL_RESOLVERS_DEBUG = True # Active only when TEMPLATE_DEBUG is True.

# A tuple that lists people who get code error notifications. When
# DEBUG=False and a view raises an exception, Django will e-mail these
# people with the full exception information. Each member of the tuple
# should be a tuple of (Full name, e-mail address).
ADMINS = ()

MANAGERS = ADMINS

# Specify the version of PostGIS installed in the nodewatcher database; this is
# required to avoid Django from raising errors about an invalid version
POSTGIS_VERSION = (2, 1)

DATABASES = {
    'default': {
        # Follow https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/ to install GeoDjango.
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'nodewatcher', # Use: createdb nodewatcher
        'USER': os.environ.get('DB_1_ENV_PGSQL_ROLE_1_USERNAME', 'nodewatcher'), # Set to empty string to connect as current user.
        'PASSWORD': os.environ.get('DB_1_ENV_PGSQL_ROLE_1_PASSWORD', ''),
        'HOST': os.environ.get('DB_1_PORT_5432_TCP_ADDR', 'localhost'), # Set to empty string for socket.
        'PORT': os.environ.get('DB_1_PORT_5432_TCP_PORT', ''), # Set to empty string for default.
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
    ('sl', _('Slovenian')),
)

LOCALE_PATHS = (
    os.path.abspath(os.path.join(settings_dir, 'locale')),
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
MEDIA_ROOT = os.path.abspath(os.path.join(settings_dir, '..', 'media'))

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
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
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
    #'django.template.loaders.eggs.Loader',
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
    'nodewatcher.core.frontend.middleware.ClientNodeMiddleware',
)

# TODO: We should not use this everywhere, only on specific views.
ATOMIC_REQUESTS = True

ROOT_URLCONF = 'nodewatcher.urls'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #os.path.join(settings_dir, 'templates'),
)

# See handler403 in urls.py as well.
CSRF_FAILURE_VIEW = 'missing.views.forbidden_view'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'

AUTH_PROFILE_MODULE = 'accounts.UserProfileAndSettings'


def user_url(user):
    from django.core import urlresolvers
    return urlresolvers.reverse('AccountsComponent:user_page', kwargs={'username': user.username})

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': user_url,
}

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN = True

# django-guardian anonymous user.
ANONYMOUS_USER_ID = -1

AUTHENTICATION_BACKENDS = (
    'nodewatcher.extra.accounts.auth.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

DEFAULT_EXCEPTION_REPORTER_FILTER = 'missing.debug.SafeExceptionReporterFilter'

TEST_RUNNER = 'nodewatcher.test_runner.FilteredTestSuiteRunner'
TEST_RUNNER_FILTER = (
    'nodewatcher.',
    'missing.',
    'django_datastream.',
)

INSTALLED_APPS = (
    # Common frontend libraries before nodewatcher.core.frontend.
    # Uses "prepend_data" to assure libraries are loaded first.
    'nodewatcher.extra.jquery',
    'nodewatcher.extra.normalize',

    # Ours are at the beginning so that we can override default templates in 3rd party Django apps.
    'nodewatcher.core',
    'nodewatcher.core.allocation',
    'nodewatcher.core.allocation.ip',
    'nodewatcher.core.events',
    'nodewatcher.core.frontend',
    'nodewatcher.core.generator.cgm',
    'nodewatcher.core.generator',
    'nodewatcher.core.monitor',
    'nodewatcher.core.registry',

    # Modules.
    'nodewatcher.modules.administration.types',
    'nodewatcher.modules.administration.projects',
    'nodewatcher.modules.administration.location',
    'nodewatcher.modules.administration.description',
    'nodewatcher.modules.administration.roles',
    'nodewatcher.modules.administration.status',
    'nodewatcher.modules.equipment.antennas',
    'nodewatcher.modules.platforms.openwrt',
    'nodewatcher.modules.devices',
    'nodewatcher.modules.monitor.sources.http',
    'nodewatcher.modules.monitor.datastream',
    'nodewatcher.modules.monitor.http.resources',
    'nodewatcher.modules.monitor.http.interfaces',
    'nodewatcher.modules.monitor.topology',
    'nodewatcher.modules.monitor.validation.reboot',
    'nodewatcher.modules.monitor.validation.version',
    'nodewatcher.modules.monitor.validation.interfaces',
    'nodewatcher.modules.routing.olsr',
    'nodewatcher.modules.routing.babel',
    'nodewatcher.modules.sensors.digitemp',
    'nodewatcher.modules.sensors.solar',
    'nodewatcher.modules.authentication.public_key',
    'nodewatcher.modules.vpn.tunneldigger',
    'nodewatcher.modules.events.sinks.db_sink',
    'nodewatcher.modules.frontend.display',
    'nodewatcher.modules.frontend.editor',
    'nodewatcher.modules.frontend.list',
    'nodewatcher.modules.frontend.mynodes',
    'nodewatcher.modules.frontend.statistics',
    'nodewatcher.modules.frontend.topology',
    'nodewatcher.modules.frontend.generator',
    'nodewatcher.modules.frontend.map',
    'nodewatcher.modules.administration.banner',
    'nodewatcher.modules.sensors.generic',

    # Defaults for wlan slovenia network.
    'nodewatcher.modules.defaults.wlansi',

    # Importers for external data.
    'nodewatcher.modules.importer.nw2',

    # Accounts support.
    'nodewatcher.extra.accounts',

    # Legacy apps for migrations.
    'nodewatcher.legacy.nodes',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'django.contrib.admin',
    'django.contrib.gis',

    # We override staticfiles runserver with default Django runserver in
    # nodewatcher.core.frontend, which is loaded before for this to work.
    'django.contrib.staticfiles',

    'tastypie',
    'django_datastream',
    'guardian',
    'sekizai', # In fact overridden by "nodewatcher.core.frontend" sekizai_tags which adds "prepend_data" and "prependtoblock"
    'missing',
    'timezone_field',
    'overextends',
    'json_field',
    'uuidfield',
    'leaflet',
    'django_countries',
    'timedelta',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '[%(levelname)s/%(name)s] %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'null': {
            'class': 'django.utils.log.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console'],
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

MONGO_DATABASE_NAME = 'nodewatcher'
MONGO_DATABASE_OPTIONS = {
    'tz_aware': USE_TZ,
}

CELERY_RESULT_BACKEND = 'mongodb'
CELERY_MONGODB_BACKEND_SETTINGS = {
    'host': os.environ.get('TOKUMX_1_PORT_27017_TCP_ADDR', '127.0.0.1'),
    'port': int(os.environ.get('TOKUMX_1_PORT_27017_TCP_PORT', '27017')),
    'database': MONGO_DATABASE_NAME,
    'taskmeta_collection': 'celery_taskmeta',
    'options': MONGO_DATABASE_OPTIONS,
}

BROKER_URL = 'mongodb://%(host)s:%(port)s/%(db)s' % {
    'host': os.environ.get('TOKUMX_1_PORT_27017_TCP_ADDR', '127.0.0.1'),
    'port': os.environ.get('TOKUMX_1_PORT_27017_TCP_PORT', '27017'),
    'db': MONGO_DATABASE_NAME,
}

CELERY_ENABLE_UTC = USE_TZ
CELERY_TIMEZONE = TIME_ZONE
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERYD_PREFETCH_MULTIPLIER = 15
CELERY_IGNORE_RESULT = True
CELERY_DEFAULT_QUEUE = 'default'

CELERY_QUEUES = {
    'default': {
        'exchange': 'default',
        'binding_key': 'default',
    },
    'generator': {
        'exchange': 'generator',
        'binding_key': 'generator',
    },
    'monitor': {
        'exchange': 'monitor',
        'binding_key': 'monitor',
    },
}

CELERY_ROUTES = {
    # Generator.
    'nodewatcher.core.generator.cgm.tasks.background_build': {
        'queue': 'generator',
    },
    # Monitoring.
    'nodewatcher.core.monitor.tasks.run_pipeline': {
        'queue': 'monitor',
    },
}

# Monitoring runs and processors configuration; this defines the order in which monitoring processors
# will be called. Multiple consecutive node processors will be automatically grouped and
# executed in parallel for all nodes that have been chosen so far by network processors. Only
# processors that are specified here will be called.
#
# Multiple runs are executed in parallel, each with its own worker pool and on a preconfigured interval.

TELEMETRY_PROCESSOR_PIPELINE = (
    # Validators should start here in order to obtain previous state.
    'nodewatcher.modules.monitor.validation.reboot.processors.RebootValidator',
    'nodewatcher.modules.monitor.validation.version.processors.VersionValidator',
    'nodewatcher.modules.monitor.validation.interfaces.processors.InterfaceValidator',
    # Telemetry processors should be below this point.
    'nodewatcher.modules.monitor.sources.http.processors.HTTPTelemetry',
    'nodewatcher.modules.monitor.http.general.processors.GeneralInfo',
    'nodewatcher.modules.monitor.http.resources.processors.SystemStatus',
    'nodewatcher.modules.monitor.http.interfaces.processors.DatastreamInterfaces',
    'nodewatcher.modules.monitor.http.clients.processors.ClientInfo',
    'nodewatcher.modules.routing.babel.processors.BabelTopology',
    'nodewatcher.modules.sensors.generic.processors.GenericSensors',
    'nodewatcher.modules.vpn.tunneldigger.processors.DatastreamTunneldigger',
    'nodewatcher.modules.administration.status.processors.NodeStatus',
    'nodewatcher.modules.monitor.datastream.processors.NodeDatastream',
)

MONITOR_RUNS = {
    'latency': {
        'workers': 10,
        'interval': 600,
        'processors': (
            'nodewatcher.modules.routing.olsr.processors.Topology',
            'nodewatcher.modules.monitor.measurements.rtt.processors.RttMeasurement',
            'nodewatcher.modules.monitor.datastream.processors.TrackRegistryModels',
            'nodewatcher.modules.monitor.measurements.rtt.processors.StoreNode',
            'nodewatcher.modules.administration.status.processors.NodeStatus',
            'nodewatcher.modules.monitor.datastream.processors.NodeDatastream',
        ),
    },

    'telemetry': {
        'workers': 30,
        'interval': 300,
        'max_tasks_per_child': 50,
        'processors': (
            'nodewatcher.core.monitor.processors.GetAllNodes',
            'nodewatcher.modules.routing.olsr.processors.Topology',
            'nodewatcher.modules.monitor.datastream.processors.TrackRegistryModels',
            'nodewatcher.modules.routing.olsr.processors.NodePostprocess',
            TELEMETRY_PROCESSOR_PIPELINE,
            'nodewatcher.modules.monitor.datastream.processors.MaintenanceBackprocess',
        ),
    },

    'telemetry-push': {
        # This run does not define any scheduling or worker information, so it will only be
        # executed on demand.
        'processors': (
            'nodewatcher.modules.monitor.sources.http.processors.HTTPGetPushedNode',
            'nodewatcher.modules.monitor.datastream.processors.TrackRegistryModels',
            TELEMETRY_PROCESSOR_PIPELINE,
        ),
    },

    'datastream': {
        'workers': 10,
        'interval': 700,
        'max_tasks_per_child': 1,
        'processors': (
            'nodewatcher.modules.monitor.datastream.processors.MaintenanceDownsample',
        ),
    },

    'topology': {
        'workers': 5,
        'interval': 60,
        'processors': (
            'nodewatcher.modules.routing.olsr.processors.Topology',
            'nodewatcher.modules.routing.olsr.processors.NodePostprocess',
            'nodewatcher.modules.monitor.topology.processors.Topology',
            'nodewatcher.modules.monitor.datastream.processors.NetworkDatastream',
        ),
    },
}

# Identifier of the run that should be used to handle HTTP pushes.
MONITOR_HTTP_PUSH_RUN = 'telemetry-push'
# Base host that should be used for HTTP push. Must be reachable from nodes.
MONITOR_HTTP_PUSH_HOST = '127.0.0.1'

# Backend for the monitoring data archive.
DATASTREAM_BACKEND = 'datastream.backends.mongodb.Backend'
# Each backend can have backend-specific settings that can be specified here.
DATASTREAM_BACKEND_SETTINGS = {
    'database_name': MONGO_DATABASE_NAME,
    'host': os.environ.get('TOKUMX_1_PORT_27017_TCP_ADDR', '127.0.0.1'),
    'port': int(os.environ.get('TOKUMX_1_PORT_27017_TCP_PORT', '27017')),
    'tz_aware': USE_TZ,
}

OLSRD_MONITOR_HOST = '127.0.0.1'
OLSRD_MONITOR_PORT = 2006

# UUID of the node that is performing measurements (usually the node where the nodewatcher
# monitor is running on).
MEASUREMENT_SOURCE_NODE = ''

# Storage for generated firmware images.
GENERATOR_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Disable South migrations during unit tests as they will fail
SOUTH_TESTS_MIGRATE = False

# In general, use https when constructing full URLs to nodewatcher?
# Django's is_secure is used in the code as well. See SECURE_PROXY_SSL_HEADER configuration option.
USE_HTTPS = False

# Server's public key. This is used for certificate pinning when provisioning nodes. If this is not
# set, nodes may be configured to access the server via insecure HTTP instead.
HTTPS_PUBLIC_KEY = None

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (46.05, 14.507),
    'DEFAULT_ZOOM': 8,
    'RESET_VIEW': False,
}

NETWORK = {
    'NAME': 'your network name',
    'HOME': 'http://example.net',
    'CONTACT': 'open@example.net',
    'CONTACT_PAGE': 'http://example.net/contact',
    'DESCRIPTION': 'open wireless network in your neighborhood',
    'FAVICON_FILE': None,
    'LOGO_FILE': None,
    'DEFAULT_PROJECT': None,
}

EVENTS_EMAIL = DEFAULT_FROM_EMAIL
IMAGE_GENERATOR_EMAIL = DEFAULT_FROM_EMAIL

FRONTEND_MAIN_COMPONENT = 'ListComponent'

MENUS = {
    #'main_menu': [
    #    {
    #        'name': ...,
    #        'weight': ...,
    #        'visible': True,
    #    },
    #],
    #'accounts_menu': [
    #    ...
    #],
}

PARTIALS = {
    #'node_snippet_partial': [
    #    {
    #        'name': ...,
    #        'weight': ...,
    #        'visible': True,
    #    }
    #],
    #'node_display_partial': [
    #    ...
    #],
}

# Allowed hosts (required for production use)
ALLOWED_HOSTS = []
