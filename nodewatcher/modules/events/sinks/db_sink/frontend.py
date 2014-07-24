from nodewatcher.core.frontend import api

from . import resources


api.v1_api.register(resources.EventResource())
