from tastypie import api

from .resources import *


v1_api = api.NamespacedApi(api_name='v1', urlconf_namespace='api')
