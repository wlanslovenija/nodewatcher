var icons = {};
var antennaOffset = 23; // antenna top is at (9, 7), icon anchor at (9, 30)

function createIcon(status) {
  if (icons[status])
    return icons[status];

  icon = new google.maps.Icon();
  icon.image = "/images/status_" + status + "_gmap.png";
  icon.shadow = "/images/gmap_node_shadow.png";
  icon.transparent = "/images/gmap_node_transparent.png";
  icon.imageMap = [12,0,14,1,15,2,16,3,16,4,16,5,17,6,17,7,17,8,16,9,16,10,16,11,15,12,14,13,13,14,14,15,14,16,15,17,15,18,16,19,16,20,16,21,17,22,17,23,18,24,18,25,19,26,19,27,15,28,16,29,14,30,5,30,3,29,4,28,0,27,1,26,1,25,1,24,2,23,2,22,3,21,3,20,4,19,4,18,4,17,5,16,5,15,6,14,5,13,4,12,3,11,3,10,3,9,2,8,2,7,2,6,3,5,3,4,3,3,4,2,5,1,7,0];
  icon.iconSize = new google.maps.Size(20, 32);
  icon.shadowSize = new google.maps.Size(32, 32);
  icon.iconAnchor = new google.maps.Point(9, 30);
  icon.infoWindowAnchor = new google.maps.Point(10, 2);
  icons[status] = icon;
  return icon;
}

function createMarker(node) {
  var opts = { "title" : node.name + " (" + node.ip + ")", "icon" : createIcon(node.status) };
  var m = new google.maps.Marker(new google.maps.LatLng(node.lat, node.long), opts);
  GEvent.addListener(m, "click", function() {
    html = "<b>" + node.name + "</b> (" + node.ip + ")<div class=\"gmap_details\">Status: <span class=\"node_status_" +
           node.status + "\">" + node.status + "</span><br><a href=\"/nodes/node/" + node.pk +"\">more information</a>";
    if (node.url) html = html + " | <a href=\"" + node.url + "\">visit home page</a>";
    m.openInfoWindowHtml(html + "</div>");
  });
  gmap.addOverlay(m);
}

function createLink(src, dst, link) {
  var projection = gmap.getCurrentMapType().getProjection();
  var startPoint = projection.fromLatLngToPixel(new google.maps.LatLng(src.lat, src.long), gmap.getZoom());
  var endPoint = projection.fromLatLngToPixel(new google.maps.LatLng(dst.lat, dst.long), gmap.getZoom());
  
  startPoint.y -= antennaOffset;
  endPoint.y -= antennaOffset;
  
  var p = new google.maps.Polyline([
    projection.fromPixelToLatLng(startPoint, gmap.getZoom()),
    projection.fromPixelToLatLng(endPoint, gmap.getZoom())
  ], link.color, 5);
  gmap.addOverlay(p);
  return { "overlay": p, "src": src, "dst": dst, "link": link };
}
