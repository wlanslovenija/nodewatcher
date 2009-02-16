from django import template
from django.template import Library
from django.template import RequestContext
from django.template import resolve_variable

register = Library()

GOOGLE_MAPS_API_KEY = "ABQIAAAAmW9WFNNiQwBMneBJZLweHBR3WYOwtT4kU6GVX3AHou_9Z28H_xQgcvQXunWn76h2_FTmY4nu0aylNg"
INCLUDE_TEMPLATE = '<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s" type="text/javascript"></script>' % GOOGLE_MAPS_API_KEY
BASIC_TEMPLATE = """
<div id="gmap" style="width: 500px; height: 300px;"></div>
<script>
  function create_map() {
    if (GBrowserIsCompatible()) {
      var map = new GMap2(document.getElementById("gmap"));
      map.setCenter(new GLatLng(%(lat)s, %(long)s), 13);
      map.enableDoubleClickZoom();
      map.addControl(new GSmallMapControl());
      var m = 0;
      if (%(marker)s && %(mlat)s > 0 && %(mlong)s > 0) {
        m = new GMarker(new GLatLng(%(mlat)s, %(mlong)s));
        map.addOverlay(m);
        map.setCenter(m.getLatLng(), 15);
      }

      GEvent.addListener(map, "click", function(overlay, p) {
        if (!m) {
          m = new GMarker(p);
          map.addOverlay(m);
        } else {
          m.setLatLng(p);
        }

        document.getElementById("id_geo_lat").value = p.lat();
        document.getElementById("id_geo_long").value = p.lng();
      });
    }
  }

  document.onload = create_map;
</script>
"""

class GMapNode(template.Node):
  def __init__(self, params):
    self.params = params
  
  def render(self, context):
    for k, v in self.params.iteritems():
      try:
        self.params[k] = resolve_variable(v, context)
      except:
        pass

      if k == 'marker':
        self.params[k] = "1" if v == 'yes' else "0"

      if self.params[k] == None:
        self.params[k] = 0
    
    return INCLUDE_TEMPLATE + (BASIC_TEMPLATE % self.params)

def do_gmap(parser, token):
  items = token.split_contents()

  # Defaults
  parameters = {
    'lat'     : 0.0,
    'long'    : 0.0,
    'mlat'    : 0.0,
    'mlong'   : 0.0,
    'marker'  : 'no'
  }

  for item in items[1:]:
    param, value = item.split(":")
    param = param.strip()
    value = value.strip()
    print param, value

    if parameters.has_key(param):
      if value[0] == '"':
        value = value[1:-1]

      parameters[param] = value
  
  return GMapNode(parameters)

register.tag('gmap', do_gmap)

