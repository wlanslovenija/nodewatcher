from django import template
from django.template import Library
from django.template import RequestContext
from django.template import resolve_variable

register = Library()

GOOGLE_MAPS_API_KEY = "ABQIAAAAmW9WFNNiQwBMneBJZLweHBQsbKtnqemGOa87hypl-SttWLUzChTDFDo3Fbn2FY6JSqvVkL_gxrQg9g"
INCLUDE_TEMPLATE = """
<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s" type="text/javascript"></script>
"""% GOOGLE_MAPS_API_KEY
BASIC_TEMPLATE = """
<div id="gmap" style="width:400px; height: 300px;"></div>
<script>
  var icons = {};

  function create_icon(status)
  {
    if (icons[status])
      return icons[status];

    icon = new GIcon();
    icon.image = "/images/status_"+status+"_gmap.png";
    icon.shadow = "/images/gmap_node_shadow.png";
    icon.transparent = "gmap_node_transparent.png";
    icon.imageMap = [12,0,14,1,15,2,16,3,16,4,16,5,17,6,17,7,17,8,16,9,16,10,16,11,15,12,14,13,13,14,14,15,14,16,15,17,15,18,16,19,16,20,16,21,17,22,17,23,18,24,18,25,19,26,19,27,15,28,16,29,14,30,5,30,3,29,4,28,0,27,1,26,1,25,1,24,2,23,2,22,3,21,3,20,4,19,4,18,4,17,5,16,5,15,6,14,5,13,4,12,3,11,3,10,3,9,2,8,2,7,2,6,3,5,3,4,3,3,4,2,5,1,7,0];
    icon.iconSize = new GSize(20, 32);
    icon.shadowSize = new GSize(32, 32);
    icon.iconAnchor = new GPoint(9, 30);
    icon.infoWindowAnchor = new GPoint(10, 2);
    icons[status] = icon;
    return icon;
  }

  function create_map() {
    if (GBrowserIsCompatible()) {
      var map = new GMap2(document.getElementById("gmap"));
      map.setCenter(new GLatLng(%(lat)s, %(long)s), 13);
      map.enableDoubleClickZoom();
      map.removeMapType(map.getMapTypes()[1]);
      map.addControl(new GSmallMapControl());
      map.addControl(new GMapTypeControl());
      var m = 0;
      if (%(marker)s && %(mlat)s > 0 && %(mlong)s > 0) {
        m = new GMarker(new GLatLng(%(mlat)s, %(mlong)s), {'icon' : create_icon("%(status)s")});
        map.addOverlay(m);
        map.setCenter(m.getLatLng(), 15);
      }

      if (%(clickable)s) {
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
  }

  $(document).ready(function() { create_map(); });
</script>
"""

FULL_TEMPLATE = """
<div id="gmap" style="width: 700px; height: 700px;"></div>
<script>
  function create_map() {
    if (GBrowserIsCompatible()) {
      var map = new GMap2(document.getElementById("gmap"));
      map.setCenter(new GLatLng(%(lat)s, %(long)s), 13);
      map.removeMapType(map.getMapTypes()[1]);
      map.enableDoubleClickZoom();
      map.addControl(new GSmallMapControl());
      map.addControl(new GMapTypeControl());

      if ("%(callback)s" != "undefined") {
        %(callback)s(map);
      }
    }
  }

  $(document).ready(function() { create_map(); });
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

      if k in ('marker', 'clickable'):
        self.params[k] = "1" if v == 'yes' else "0"

      if self.params[k] == None:
        self.params[k] = 0
    
    if self.params['full'] == "yes":
      return INCLUDE_TEMPLATE + (FULL_TEMPLATE % self.params)
    else:
      return INCLUDE_TEMPLATE + (BASIC_TEMPLATE % self.params)

def do_gmap(parser, token):
  items = token.split_contents()

  # Defaults
  parameters = {
    'lat'       : 0.0,
    'long'      : 0.0,
    'mlat'      : 0.0,
    'mlong'     : 0.0,
    'marker'    : 'no',
    'clickable' : 'yes',
    'full'      : 'no',
    'callback'  : 'undefined',
    'status'  : 'up'
  }

  for item in items[1:]:
    param, value = item.split(":")
    param = param.strip()
    value = value.strip()

    if parameters.has_key(param):
      if value[0] == '"':
        value = value[1:-1]

      parameters[param] = value
  
  return GMapNode(parameters)

register.tag('gmap', do_gmap)

