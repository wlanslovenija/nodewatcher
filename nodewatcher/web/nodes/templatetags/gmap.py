from django import template
from django.conf import settings
from django.template import Library
from django.template import RequestContext
from django.template import resolve_variable

register = Library()

import sys

@register.inclusion_tag('gmap.js')
def do_gmap(callback=None, full=False, mlat=0.0, mlong=0.0, clickable=True, status='up'):
  return {
    'google_key': settings.GOOGLE_MAPS_API_KEY,
    'lat': settings.GOOGLE_MAPS_DEFAULT_LAT,
    'long': settings.GOOGLE_MAPS_DEFAULT_LONG,
    'zoom': settings.GOOGLE_MAPS_DEFAULT_ZOOM,
    'node_zoom': settings.GOOGLE_MAPS_DEFAULT_NODE_ZOOM,
    'mlat': mlat,
    'mlong': mlong,
    'clickable': clickable,
    'full': full,
    'callback': callback,
    'status': status          
  }
