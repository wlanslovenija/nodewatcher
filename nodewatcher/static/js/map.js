var updating = false;
var centering = false;
var visibleNodes = 0;
var shownNodes = {};
var shownNodesNumber = 0;
var shownLinks = [];

var gmap;

function updateNodes(filtersNotChanged, zoomNotChanged, notMoved) {
  if (!filtersNotChanged) {
    gmap.clearOverlays();
    
    shownNodes = {};
    shownNodesNumber = 0;
    shownLinks = [];
    for (var i = 0; i < nodes.length; i++) {
      if ($('#gmap_project_' + nodes[i].project + ':checked').length == 0) continue;
      if ($('#gmap_status_' + nodes[i].status + ':checked').length == 0) continue;
      
      shownNodes[nodes[i].ip] = nodes[i];
      shownNodesNumber++;
      createMarker(nodes[i]);
    }
    
    for (var i = 0; i < links.length; i++) {
      if (shownNodes[links[i].src] && shownNodes[links[i].dst]) {
        shownLinks.push(createLink(shownNodes[links[i].src], shownNodes[links[i].dst], links[i]));
      }
    }
  }
  else if (!zoomNotChanged) {
    var newShownLinks = [];
    for (var i = 0; i < shownLinks.length; i++) {
      gmap.removeOverlay(shownLinks[i].overlay);
      newShownLinks.push(createLink(shownLinks[i].src, shownLinks[i].dst, shownLinks[i].link));
    }
    shownLinks = newShownLinks;
  }
  
  var bounds = gmap.getBounds();
  visibleNodes = 0;
  for (var node in shownNodes) {
     if (bounds.containsLatLng(new google.maps.LatLng(shownNodes[node].lat, shownNodes[node].long))) visibleNodes++;
  }
  
  $('#gmap_statusbar').html("Visible " + visibleNodes + " of " + shownNodesNumber + " shown nodes" + (shownNodesNumber != nodes.length ? " (from " + nodes.length + " all nodes)" : ""));
}

function buildHash(lat, long, zoom) {
  var hash = "lat=" + lat + "&long=" + long + "&zoom=" + zoom + "&type=" + gmap.getCurrentMapType().getUrlArg();
  hash += "&project=" + $('input[name="gmap_project"]:checked').map(function () { return $(this).val(); }).get().join(",");
  hash += "&status=" + $('input[name="gmap_status"]:checked').map(function () { return $(this).val(); }).get().join(",");
  return hash;
}

function centerMap() {
  var id = $('#gmap_center').val();
  
  if (!id) return;
  
  var bounds = new google.maps.LatLngBounds();
  for (var i = 0; i < nodes.length; i++) {
    if (nodes[i].project == id) bounds.extend(new google.maps.LatLng(nodes[i].lat, nodes[i].long));
  }
  
  var zoom = gmap.getBoundsZoomLevel(bounds);
  var filtersNotChanged = true;
  
  if ($('#gmap_project_' + id + ':checked').length == 0) {
    updating = true;
  
    $('#gmap_project_' + id).attr('checked', 'checked');
  
    updating = false;
    
    filtersNotChanged = false;
  }
  
  $('#gmap_center_default').attr('disabled', 'disabled');
  
  centering = true;
  
  $.history.load(buildHash(bounds.getCenter().lat(), bounds.getCenter().lng(), zoom), { "filtersNotChanged": filtersNotChanged, "zoomNotChanged": gmap.getZoom() == zoom ? true : false, "notMoved": false });
  
  centering = false;
}

function updateMap(changeData) {
  if (updating) return;
  
  $.history.load(buildHash(gmap.getCenter().lat(), gmap.getCenter().lng(), gmap.getZoom()), changeData);
}

function mapInit(map) {
  gmap = map;
  
  google.maps.Event.addListener(map, "zoomend", function () { updateMap( { "filtersNotChanged": true, "zoomNotChanged": false, "notMoved": true } ); });
  google.maps.Event.addListener(map, "moveend", function () { updateMap( { "filtersNotChanged": true, "zoomNotChanged": true, "notMoved": false } ); });
  google.maps.Event.addListener(map, "maptypechanged", function () { updateMap( { "filtersNotChanged": true, "zoomNotChanged": true, "notMoved": true } ); });
  
  var lock = false;
  google.maps.Event.addListener(map, "move", function () {
    // JS events hopefully execute in one thread so there is no race condition
    // but it also does not really matter if it is
    if (!lock) {
      lock = true;
      // We allow updates to occur at least 100 ms apart
      setTimeout(function () { lock = false; }, 100);
      updateMap( { "filtersNotChanged": true, "zoomNotChanged": true, "notMoved": false } );
    }
  });

  $(document).ready(function () {
    $('#gmap_center').change(function () { centerMap(); });
    $('input[name="gmap_project"]').change(function () { updateMap( { "filtersNotChanged": false, "zoomNotChanged": true, "notMoved": true } ); });
    $('input[name="gmap_status"]').change(function () { updateMap( { "filtersNotChanged": false, "zoomNotChanged": true, "notMoved": true } ); });
    
    var oldhash = "";
    $.history.init(function (hash, changeData) {
      if (!changeData) changeData = {};
      
      if (!changeData.notMoved || !changeData.zoomNotChanged) {
        if (!centering) {
          $('#gmap_center_default').removeAttr('disabled');
          $('#gmap_center').val("");
        }
      }
      
      if (hash) {
        if (hash == oldhash) {
          return;
        }
        else {
          oldhash = hash;
        }
        
        var splits = hash.split(/&/);
        if (splits.length == 0) {
          udpate_map();
          return;
        }
        
        var params = {
          "lat": gmap.getCenter().lat(),
          "long": gmap.getCenter().lng(),
          "zoom": gmap.getZoom(),
          "type": gmap.getCurrentMapType().getUrlArg(),
          "project": [],
          "status": []
        };
        
        for (var i = 0; i < splits.length; i++) {
          var sp = splits[i].split(/=/);
          if (sp.length == 2) {
            if (sp[0] == "project") {
              params.project = $.grep(sp[1].split(/,/), function (el, i) { return $('#gmap_project_' + el).attr('disabled'); }, true);
            }
            else if (sp[0] == "status") {
              params.status = sp[1].split(/,/);
            }
            else {
              params[sp[0]] = sp[1];
            }
          }
        }
        
        var mapType = gmap.getCurrentMapType();
        var mapTypes = gmap.getMapTypes();
        for (var m = 0; m < mapTypes.length; m++) {
          if (mapTypes[m].getUrlArg() == params.type) {
            mapType = mapTypes[m];
            break;
          }
        }
        
        updating = true;
        
        gmap.setCenter(new google.maps.LatLng(params.lat, params.long), parseInt(params.zoom), mapType);
        
        $('input[name="gmap_project"]').val(params.project);
        $('input[name="gmap_status"]').val(params.status);
        
        updating = false;
        
        updateNodes(changeData.filtersNotChanged, changeData.zoomNotChanged, changeData.notMoved);
      }
      else {
        updateMap( { "filtersNotChanged": false, "zoomNotChanged": false, "notMoved": false } );
      }
    });
  });
}
