# Development Django settings for nodewatcher project.

import os.path
database_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db.sqlite').replace('\\', '/')
template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates').replace('\\', '/')

STATIC_DOC_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static').replace('\\', '/')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# A tuple that lists people who get code error notifications. When
# DEBUG=False and a view raises an exception, Django will e-mail these
# people with the full exception information. Each member of the tuple
# should be a tuple of (Full name, e-mail address).
ADMINS = ()

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = database_file  # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

EMAIL_HOST = 'localhost'
EMAIL_SUBJECT_PREFIX = '[wlan-lj] '

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
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1p)^zvjul0^c)v5*l!8^48g=ili!cn54^l)wl1avvu-x$==k7p'

# Google Maps API key for 127.0.0.1
GOOGLE_MAPS_API_KEY = 'ABQIAAAAsSAo-sxy6T5T7_DN1d9N4xRi_j0U6kJrkFvY4-OX2XYmEAa76BRH5tgaUAj1SaWR_RbmjkZ4zO7dDA'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.load_template_source',
  'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.csrf.middleware.CsrfMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'wlanlj.urls'

TEMPLATE_DIRS = (
  # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
  template_dir,
)

DATE_FORMAT = 'Y-m-d H:i:s'
FORCE_SCRIPT_NAME = ''
LOGIN_REDIRECT_URL = '/nodes/my_nodes'
LOGIN_URL = '/auth/login'
AUTH_PROFILE_MODULE = 'account.useraccount'
AUTHENTICATION_BACKENDS = (
  'wlanlj.account.auth.CryptBackend',
)

INSTALLED_APPS = (
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.sitemaps',
  'wlanlj.nodes',
  'wlanlj.generator',
  'wlanlj.account',
  'wlanlj.dns',
  'wlanlj.policy',
)

# Graph configuration
GRAPH_DIR = os.path.join(STATIC_DOC_ROOT, 'graphs').replace('\\', '/')
GRAPH_TIMESPANS = (
  ('day',   86400),
  ('week',  604800),
  ('month', 2678400),
  ('year',  33053184)
)
