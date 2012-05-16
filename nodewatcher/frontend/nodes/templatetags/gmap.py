from django.conf import settings
from django.template import Library

register = Library()

@register.inclusion_tag('gmap.js', takes_context=True)
def do_gmap(context, callback=None, click_callback=None, full=False, marker_lat=None, marker_long=None, clickable=True, status='up'):
  """
  Renders Google Maps JavaScript code.
  
  @param callback: Name of the callback function to call at the end of Google Maps initialization
  @param click_callback: Name of the callbak function to call on every click on Google Maps
  @parm full: Draw full map or only small map around optional marker
  @param marker_lat: Optional marker to draw - latitude
  @param marker_long: Optional marker to draw - longitude
  @param clickable: Is map clickable - when the user clicks marker is put and `id_geo_lat` and `id_geo_long` page elements are updated
  @param status: Status of optional marker
  """
  context.update({
    'google_key': settings.GOOGLE_MAPS_API_KEY,
    'lat': settings.GOOGLE_MAPS_DEFAULT_LAT,
    'long': settings.GOOGLE_MAPS_DEFAULT_LONG,
    'zoom': settings.GOOGLE_MAPS_DEFAULT_ZOOM,
    'node_zoom': settings.GOOGLE_MAPS_DEFAULT_NODE_ZOOM,
    'marker_lat': marker_lat,
    'marker_long': marker_long,
    'clickable': clickable,
    'full': full,
    'callback': callback,
    'click_callback': click_callback,
    'status': status          
  })
  return context
