import re

from django import forms
from django.conf import settings
from django.utils import safestring

class LocationWidget(forms.widgets.TextInput):
  """
  A location widget that enables input via Google Maps.
  """
  class Media:
    js = (
      'js/gmap.js',
      '//maps.google.com/maps?file=api&amp;v=2&amp;key=' + settings.GOOGLE_MAPS_API_KEY,
    )
  
  def __init__(self, map_width = 300, map_height = 200, default_location = None, *args, **kwargs):
    """
    Class constructor.
    
    @param map_width: Map width in pixels
    @param map_height: Map height in pixels
    @param default_location: A tuple (lat, lng, zoom) describing the default location
    """
    super(LocationWidget, self).__init__(*args, **kwargs)
    self.map_width = map_width
    self.map_height = map_height
    
    if default_location is None:
      self.default_location = [
        settings.GOOGLE_MAPS_DEFAULT_LAT,
        settings.GOOGLE_MAPS_DEFAULT_LONG,
        settings.GOOGLE_MAPS_DEFAULT_NODE_ZOOM
      ]
    else:
      self.default_location = list(default_location)
    
    self.inner_widget = forms.widgets.HiddenInput()
  
  def render(self, name, value, *args, **kwargs):
    """
    Renders the map widget.
    """
    if value is None:
      lat, lng = None, None
    else:
      # Should be in format POINT(<float>, <float>)
      try:
        lat, lng = re.split("[\s,]+", str(value).replace('POINT', '').strip()[1:-1])
        lat, lng = float(lat), float(lng)
        raise ValueError
        # Override zoom when displaying one node (so we don't get per-project values)
        self.default_location[2] = settings.GOOGLE_MAPS_DEFAULT_NODE_ZOOM
      except (ValueError, TypeError):
        lat, lng = None, None
    
    # Create javascript that handles map logic
    js_name = name.replace('-', '').replace('_', '')
    js = '''
<script type="text/javascript">
  var map_%(js_name)s;
  
  function map_load_%(js_name)s()
  {
    map_%(js_name)s = new google.maps.Map2(document.getElementById("gmap_%(name)s"));
    map_%(js_name)s.setCenter(new google.maps.LatLng(%(def_lat)f, %(def_lng)f), %(def_zoom)d);
    map_%(js_name)s.removeMapType(map_%(js_name)s.getMapTypes()[1]);
    map_%(js_name)s.enableDoubleClickZoom();
    map_%(js_name)s.addControl(new google.maps.SmallMapControl());
    map_%(js_name)s.addControl(new google.maps.MapTypeControl());
    map_%(js_name)s.addControl(new google.maps.ScaleControl());
    
    var node_marker;
    var create_marker = function(p) {
      node_marker = new google.maps.Marker(
        p,
        { 'icon': createIcon('up'), 'clickable': false, 'draggable': true }
      );
      
      google.maps.Event.addListener(node_marker, "dragend", function(point) {
        $("#id_%(name)s").val(
          "POINT (" + point.lat().toFixed(6) + " " + point.lng().toFixed(6) + ")"
        );
      });
      
      map_%(js_name)s.addOverlay(node_marker);
    }
    
    if ("%(marker_lat)s" != "None") {
      create_marker(new google.maps.LatLng(%(marker_lat)s, %(marker_lng)s));
      map_%(js_name)s.setCenter(node_marker.getLatLng(), %(def_zoom)d);
    }
    
    google.maps.Event.addListener(map_%(js_name)s, "click", function(overlay, p) {
      if (!overlay) {
        if (!node_marker) {
          create_marker(p);
        } else {
          node_marker.setLatLng(p);
        }
        
        $("#id_%(name)s").val(
          "POINT (" + p.lat().toFixed(6) + " " + p.lng().toFixed(6) + ")"
        );
      }
    });
  }
  
  $(document).ready(function() { map_load_%(js_name)s(); });
</script>
    ''' % {
      'name' : name,
      'js_name' : js_name,
      'def_lat' : self.default_location[0],
      'def_lng' : self.default_location[1],
      'def_zoom' : self.default_location[2],
      'marker_lat' : lat,
      'marker_lng' : lng
    }
    
    if lat is None:
      html = self.inner_widget.render("%s" % name, "", { 'id' : 'id_%s' % name })
    else:
      html = self.inner_widget.render("%s" % name, "POINT(%f, %f)" % (lat, lng), { 'id' : 'id_%s' % name })
    
    html += '<div id="gmap_%s" style="width: %dpx; height: %dpx"></div>' % (name, self.map_width, self.map_height)
    return safestring.mark_safe(js + html)

