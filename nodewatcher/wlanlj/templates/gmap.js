<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key={{ google_key|escape }}" type="text/javascript"></script>
<script src="/js/gmap.js" type="text/javascript"></script>
<script type="text/javascript">
/* <![CDATA[ */
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
      var m = null;
      {% if mlat and mlong %}
      m = new google.maps.Marker(new google.maps.LatLng({{ mlat }}, {{ mlong }}), {'icon': createIcon('{{ status|escapejs }}')});
      map.addOverlay(m);
      map.setCenter(m.getLatLng(), {{ node_zoom }});
      {% endif %}

      {% if clickable %}
      google.maps.Event.addListener(map, "click", function(overlay, p) {
        if (!m) {
          m = new google.maps.Marker(p, {'icon': createIcon('new')});
          map.addOverlay(m);
        }
        else {
          m.setLatLng(p);
        }

        document.getElementById("id_geo_lat").value = p.lat();
        document.getElementById("id_geo_long").value = p.lng();
      });
      {% endif %}
      {% endif %}
      
      if (typeof {{ callback }} == "function") {
        {{ callback }}(map);
      }
    }
  }

  $(document).ready(function() { createMap(); });
/* ]]> */
</script>
