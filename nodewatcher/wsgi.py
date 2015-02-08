"""
WSGI config for nodewatcher project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
from django.core import wsgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nodewatcher.settings")

application = wsgi.get_wsgi_application()
