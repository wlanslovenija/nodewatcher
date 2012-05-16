<script src="https://maps.google.com/maps?file=api&amp;v=2&amp;key={{ google_key|escape }}" type="text/javascript"></script>
<script src="{{ MEDIA_URL }}js/gmap.js" type="text/javascript"></script>
<script type="text/javascript">
/* <![CDATA[ */
  var nodeMarker;
  var clickEnabled;

  function putMarker(map, point) {
    if (!nodeMarker) {
      nodeMarker = new google.maps.Marker(point, {'icon': createIcon('new'), 'clickable': false, 'draggable': true});
      google.maps.Event.addListener(nodeMarker, "dragend", function(point) {
        $('#id_geo_lat').val(point.lat());
        $('#id_geo_long').val(point.lng());
      });
      map.addOverlay(nodeMarker);
    }
    else {
      nodeMarker.setLatLng(point);
    }
    
    $('#id_geo_lat').val(point.lat());
    $('#id_geo_long').val(point.lng());
  }

  function createMap() {
    if (google.maps.BrowserIsCompatible()) {
      var map = new google.maps.Map2(document.getElementById("gmap"));
      map.setCenter(new google.maps.LatLng({{ lat }}, {{ long }}), {{ zoom }});
      map.removeMapType(map.getMapTypes()[1]);
      map.enableDoubleClickZoom();
      map.addControl(new google.maps.SmallMapControl());
      map.addControl(new google.maps.MapTypeControl());
      map.addControl(new google.maps.ScaleControl());
      
      {% if not full %}
      {% if marker_lat and marker_long %}
      nodeMarker = new google.maps.Marker(new google.maps.LatLng({{ marker_lat }}, {{ marker_long }}), {'icon': createIcon('{{ status|escapejs }}')});
      map.addOverlay(nodeMarker);
      map.setCenter(nodeMarker.getLatLng(), {{ node_zoom }});
      {% endif %}

      {% if clickable %}
      google.maps.Event.addListener(map, "click", function(overlay, p) {
        if (!overlay && clickEnabled) {
          putMarker(map, p);
          {% if click_callback %}
          if (typeof {{ click_callback }} == "function") {
            {{ click_callback }}(map, p);
          }
          {% endif %}
        }
      });
      clickEnabled = true;
      {% endif %}
      {% endif %}
      
      {% if callback %}
      if (typeof {{ callback }} == "function") {
        {{ callback }}(map);
      }
      {% endif %}
    }
  }

  $(document).ready(function() { createMap(); });
/* ]]> */
</script>
