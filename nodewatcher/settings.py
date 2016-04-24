# -*- coding: utf-8 -*-
# pylint: skip-file
#
# Development Django settings for nodewatcher project.

import os

settings_dir = os.path.abspath(os.path.dirname(__file__))

# Dummy function, so that "makemessages" can find strings which should be translated.
_ = lambda s: s

DEBUG = True
TEMPLATE_DEBUG = False
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
    os.path.abspath(os.path.join(settings_dir, 'core', 'frontend', 'static')),
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

STATICFILES_STORAGE = 'nodewatcher.core.frontend.staticfiles.storage.FilesProcessorStorage'

GEOIP_PATH = os.path.abspath(os.path.join(settings_dir, '..', 'libs', 'geoip'))
DEFAULT_COUNTRY = 'SI'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1p)^zvjul0^c)v5*l!8^48g=ili!cn54^l)wl1avvu-x$==k7p'

EMAIL_HOST = 'localhost'
EMAIL_SUBJECT_PREFIX = '[nodewatcher] '
DEFAULT_FROM_EMAIL = 'webmaster@example.net'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
                'nodewatcher.core.frontend.context_processors.global_vars',
            ],
            'builtins': [
                'missing.templatetags.context_tags',
            ],
        }
    },
]

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
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

# See handler403 in urls.py as well.
CSRF_FAILURE_VIEW = 'missing.views.forbidden_view'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'


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

    # Extend the default frontend with skyline banner
    'nodewatcher.modules.frontend.skyline',

    # Ours are at the beginning so that we can override default templates in 3rd party Django apps.
    'nodewatcher.core',
    'nodewatcher.core.allocation',
    'nodewatcher.core.allocation.ip',
    'nodewatcher.core.api',
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
    'nodewatcher.modules.identity.base',
    'nodewatcher.modules.identity.public_key',
    'nodewatcher.modules.qos.base',
    'nodewatcher.modules.monitor.sources.http',
    'nodewatcher.modules.monitor.datastream',
    'nodewatcher.modules.monitor.http.resources',
    'nodewatcher.modules.monitor.http.interfaces',
    'nodewatcher.modules.monitor.http.clients',
    'nodewatcher.modules.monitor.topology',
    'nodewatcher.modules.monitor.unknown_nodes',
    'nodewatcher.modules.monitor.validation.reboot',
    'nodewatcher.modules.monitor.validation.version',
    'nodewatcher.modules.monitor.validation.interfaces',
    'nodewatcher.modules.services.dns',
    'nodewatcher.modules.services.dhcp',
    'nodewatcher.modules.services.nodeupgrade',
    'nodewatcher.modules.services.watchdog',
    'nodewatcher.modules.routing.olsr',
    'nodewatcher.modules.routing.babel',
    'nodewatcher.modules.authentication.public_key',
    'nodewatcher.modules.vpn.tunneldigger',
    'nodewatcher.modules.events.sinks.db_sink',
    'nodewatcher.modules.frontend.api',
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
    'nodewatcher.modules.defaults.network_profile',

    # OAuth2 authentication.
    'nodewatcher.modules.authentication.oauth.apps.OAuthAuthenticationConfig',
    'nodewatcher.modules.authentication.oauth.apps.OAuth2ProviderConfig',

    # Defaults for wlan slovenia network.
    'nodewatcher.extra.wlansi',

    # IRNAS extra modules.
    'nodewatcher.extra.irnas.koruza',

    # Importers for external data.
    'nodewatcher.modules.importer.nw2',

    # Accounts support.
    'nodewatcher.extra.accounts',

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

    'polymorphic',
    'tastypie',
    'django_datastream',
    'guardian',
    'sekizai', # In fact overridden by "nodewatcher.core.frontend" sekizai_tags which adds "prepend_data" and "prependtoblock"
    'missing',
    'timezone_field',
    'jsonfield',
    'leaflet',
    'django_countries',
    'timedelta',
    'registration',
    'rest_framework',
    'rest_framework_gis',
    'corsheaders',
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
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
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

BROKER_URL = 'redis://%(host)s:%(port)s/0' % {
    'host': os.environ.get('REDIS_1_PORT_6379_TCP_ADDR', '127.0.0.1'),
    'port': os.environ.get('REDIS_1_PORT_6379_TCP_PORT', '6379'),
}
CELERY_RESULT_BACKEND = BROKER_URL

CELERY_ENABLE_UTC = USE_TZ
CELERY_TIMEZONE = TIME_ZONE
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERYD_PREFETCH_MULTIPLIER = 15
CELERY_IGNORE_RESULT = True
CELERY_DEFAULT_QUEUE = 'default'
CELERYBEAT_SCHEDULE = {}

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
    'nodewatcher.core.monitor.processors.GeneralInfo',
    'nodewatcher.modules.monitor.http.resources.processors.SystemStatus',
    'nodewatcher.modules.monitor.http.interfaces.processors.DatastreamInterfaces',
    'nodewatcher.modules.monitor.http.clients.processors.ClientInfo',
    'nodewatcher.modules.routing.olsr.processors.NodeTopology',
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
            'nodewatcher.modules.routing.olsr.processors.GlobalTopology',
            'nodewatcher.modules.routing.babel.processors.IncludeRoutableNodes',
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
            'nodewatcher.modules.routing.olsr.processors.GlobalTopology',
            'nodewatcher.modules.routing.babel.processors.IncludeRoutableNodes',
            'nodewatcher.modules.monitor.datastream.processors.TrackRegistryModels',
            'nodewatcher.modules.routing.olsr.processors.NodeTopology',
            TELEMETRY_PROCESSOR_PIPELINE,
            'nodewatcher.modules.monitor.datastream.processors.MaintenanceBackprocess',
            'nodewatcher.modules.administration.status.processors.PushNodeStatus',
        ),
    },

    'telemetry-push': {
        # This run does not define any scheduling or worker information, so it will only be
        # executed on demand.
        'processors': (
            'nodewatcher.modules.monitor.unknown_nodes.processors.DiscoverUnknownNodes',
            'nodewatcher.modules.monitor.sources.http.processors.HTTPGetPushedNode',
            'nodewatcher.modules.identity.public_key.processors.VerifyNodePublicKey',
            'nodewatcher.modules.monitor.datastream.processors.TrackRegistryModels',
            TELEMETRY_PROCESSOR_PIPELINE,
        ),
    },

    'datastream': {
        'workers': 2,
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
            'nodewatcher.modules.routing.olsr.processors.GlobalTopology',
            'nodewatcher.modules.routing.olsr.processors.NodeTopology',
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
    'database_name': 'nodewatcher',
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

# Nodeupgrade server location. Note that all this information (including the private key)
# can be made public and does not need to be protected as it is only used to download
# files via SCP.
NODEUPGRADE_SERVER = ''
NODEUPGRADE_PORT = 28932
NODEUPGRADE_USER = 'fileserver'
# Private key must be in Dropbear-compatible format and base64 encoded.
NODEUPGRADE_PRIVATE_KEY = ''
# Server public key must be in SSH-compatible format.
NODEUPGRADE_SERVER_PUBLIC_KEY = ''

LEAFLET_CONFIG = {
    'TILES': [
        # OpenStreetMap.
        (
            _('OSM'),
            '//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        ),
    ],
    'DEFAULT_CENTER': (46.05, 14.507),
    'DEFAULT_ZOOM': 8,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,
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
}

EVENTS_EMAIL = DEFAULT_FROM_EMAIL
IMAGE_GENERATOR_EMAIL = DEFAULT_FROM_EMAIL

FRONTEND_MAIN_COMPONENT = 'ListComponent'

MENUS = {
    'main_menu': [
        {
            'name': 'Node List',
            'weight': 10,
            'visible': True,
        },
        {
            'name': 'Network Statistics',
            'weight': 20,
            'visible': True,
        },
        {
            'name': 'Events',
            'weight': 30,
            'visible': True,
        },
        {
            'name': 'Network Topology',
            'weight': 40,
            'visible': True,
        },
        {
            'name': 'Map',
            'weight': 50,
            'visible': True,
        },
        {
            'name': 'API',
            'weight': 60,
            'visible': True,
        },
    ],
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

# Configure which registry items should be displayed in the editor when the simple mode
# is enabled. Items should be specified for each registration point.
REGISTRY_SIMPLE_MODE = {
    'node.config': {
        'default': True,
        'items': [
            'core.general',
            'core.location',
            'core.description',
            'core.authentication',
        ],
    },
}

# REST framework.
REST_FRAMEWORK = {
    'PAGE_SIZE': 50,
    'DEFAULT_PAGINATION_CLASS': 'nodewatcher.core.api.pagination.LimitOffsetPagination',
    'DEFAULT_RENDERER_CLASSES': (
        #'rest_framework.renderers.JSONRenderer',
        'nodewatcher.core.api.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        #'rest_framework.parsers.JSONParser',
        'nodewatcher.core.api.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
}

CORS_ORIGIN_ALLOW_ALL = True
# Currently only v2 API needs this. Tastypie API provides headers by itself.
CORS_URLS_REGEX = r'^/api/v2/'
# API is read-only for now.
CORS_ALLOW_METHODS = (
    'GET',
    'HEAD',
    'OPTIONS',
)
